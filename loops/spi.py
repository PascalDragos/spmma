import math

import logging
from logging.handlers import TimedRotatingFileHandler

import colorsys
from PIL import Image, ImageDraw, ImageFont
import ST7735


# Logger
l_format = logging.Formatter('%(levelname)s : %(asctime)s %(message)s')  # formatul unei inregistrari
logger = logging.getLogger("spi")  # instanta de logger
logger.setLevel(logging.DEBUG) # afisez informatiile de la debug in sus
handler = TimedRotatingFileHandler('logs/spi.log', when="midnight", interval=1, encoding='utf8')  # in fiecare zi, alt fisier
handler.setFormatter(l_format) 
handler.prefix = "%Y-%m-%d"  # prefixul pentru un fisier
logger.addHandler(handler)


# Consumer 1
def spi_loop(q):
    try:
        print("SPI loop starts...")
        logger.debug("SPI loop starts...")
        disp = ST7735.ST7735(port=0, # SPI port number
                             cs=1, # SPI chip-select number: 0 or 1 for BCM
                             backlight=12, # Pin for controlling backlight
                             rotation=90,  # pozitia naturala a ecranului e pe verticala
                             spi_speed_hz=10_000_000, # SPI speed (in Hz)
                             dc=9)
        disp.begin()
        WIDTH = disp.width
        HEIGHT = disp.height

        logger.debug("SPI objects created")
        
        font_size = 20
        # Font optimizat pentru ecrane mici, by Intel
        font = ImageFont.truetype("ttf/ClearSans-Regular.ttf", font_size)

        img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # trebuie si in spmma cunoscute cheile acestui dictionar
        info_structure = {
             "t":    {"unit": "°C",   "min": 20,      "max": 30},
             "h":    {"unit": "%",   "min": 20,      "max": 70},
             "l":    {"unit": "lux", "min": 0,      "max": 250},
             "s":    {"unit": "db",  "min": 10,      "max": 90},
             "ox":   {"unit": "%",   "min": 14_000, "max": 24_000},
             "red":  {"unit": "%",   "min": 300_000, "max": 600_000},
             "nh3":  {"unit": "%",   "min": 80_000, "max": 110_000}
        }

        # dictionar {marime_masurata: lista ultimelor valori}
        values = {}  
        for variable in info_structure:
            values[variable] = [0] * WIDTH

        while True:
            (variable, data) = q.get()
            logger.info((variable, data))
            
            if variable == "sleep":
                disp.set_backlight(data)  # True or false
                continue
       
            # Pastreaza ultimele WIDTH valori
            # O scot pe cea mai vecche, o adaug pe cea mai noua
            values[variable] = values[variable][1:] + [data]

            # Scalare intre [0, 1]
            local_min = min(values[variable])
            local_max = max(values[variable])

            global_min = info_structure[variable]["min"]
            global_max = info_structure[variable]["max"]

            if local_min != 0:
                vmin = min(local_min, global_min)
            else:
                vmin = global_min

            vmax = max(local_max, global_max)

            colours = []
            for v in values[variable]:
                if v == 0:
                    colours.append(0)
                else:
                    colours.append((v - vmin + 1) / (vmax - vmin + 1))

            unit = info_structure[variable]["unit"]

            message = ""
            if variable in ["ox", "red", "nh3"]:
                result = list(filter(lambda x: (x != 0), values[variable]))

                avg = sum(result) / len(result)
                # avg = (min(result)+max(result))/2

                avg = avg if avg != 0 else data # pentru primul esantion
                data = round((data - avg)/avg * 100, 2)
                
                if variable in ["red", "nh3"]:
                    data = -data
                
                msg = ""
                if data > 0:
                    msg = "+"
                message = f"  {variable}: {msg}{data} {unit}"

            else:  # nu sunt gaze
                message = f"  {variable}: {data:.1f} {unit}"

            # Tot ecranul negru (fundaulul) 
            draw.rectangle((0, 0, WIDTH, HEIGHT), (0, 0, 0))

            # Latimea dreptunghiului peste care va fi text
            graph_top_point = 25
            # print(unit)
            # print(data)
            # print(vmin)
            # print(vmax)

            line_y = 0 # coordonata y a puncutului 
            for i in range(len(colours)):
                if(colours[i] == 0):
                    # primele momente cand se deschide aplicatia
                    r, g, b = 0, 0, 0
                else:
                    # Marimile trecute intr-un heatmap albastru-rosu
                    # HSV: 0 = rosu, 1.0 rosu, 0.3 verde, 0.6 albastru
                    
                    if(variable in ["red", "nh3"]):  # rezistenta mica => concentratie mare
                        # scalez in intervalul (0,1] => [0, 0.3]
                        colour = colours[i] * 0.3
                        # Punct negru pentru valoarea curenta
                        line_y = HEIGHT - ((1 - colours[i]) * (HEIGHT - graph_top_point))                        
                    else:
                        # scalez in intervalul (0,1] => [0.3, 0)
                        colour = (1.0 - colours[i]) * 0.3
                        # Punct negru pentru valoarea curenta
                        line_y = HEIGHT - (colours[i] * (HEIGHT - graph_top_point))
                    
                    # schimb hue, saturatie si luminanta maxima
                    r, g, b = [int(x * 255.0) for x in colorsys.hsv_to_rgb(colour, 1.0, 1.0)]

                # Dreptunghi de latime 1 de culoarea potrivita pentru valoarea curenta
                draw.rectangle((i, graph_top_point, i + 1, HEIGHT), (r, g, b))

                # Punct (1x3 de fapt) negru pentru valoarea curenta
                draw.rectangle((i, line_y-1, i + 1, line_y + 1), (0, 0, 0))

            # Afisarea in text a marimii si valorii curente
            draw.text((0, 0), message, font=font, fill=(255, 255, 255))

            disp.display(img)

    except KeyboardInterrupt:
        print("SPI loop stops...")
        logger.debug("SPI loop stops...\n")
