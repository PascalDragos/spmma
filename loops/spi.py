import logging
from logging.handlers import TimedRotatingFileHandler

import colorsys
from PIL import Image, ImageDraw, ImageFont
import ST7735


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
        disp = ST7735.ST7735(port=0, cs=1, backlight=12, rotation=90, spi_speed_hz=10000000, dc=9)
        disp.begin()
        WIDTH = disp.width
        HEIGHT = disp.height

        logger.debug("SPI objects created")
        
        font_size = 20
        # Font optimizat pentru ecrane mici, by Intel
        font = ImageFont.truetype("ttf/ClearSans-Regular.ttf", font_size)

        img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        variables = ["t",  "p", "h", "l", "ox", "red", "nh3"]
        unit = {"t":"C",  "p": "hPa", "h":"%", "l":"lux", "ox": "kO", "red": "kO", "nh3":"kO"}
        values = {}  # dictionar {marime_masurata: lista ultimelor valori}
        vmin = {}
        vmax = {}

        for v in variables:
            values[v] = [0] * WIDTH
            vmin[v] = float("inf")
            vmax[v] = float("-inf")

        while True:
            (variable, data) = q.get()
            logger.info((variable, data))
            if variable == "sleep":
                disp.set_backlight(data)
                continue
            # data = data - 8
            # Pastreaza ultimele WIDTH valori
            values[variable] = values[variable][1:] + [data]
            
            # Scalare intre [0, 1]
            vmin = min(values[variable])
            vmax = max(values[variable])
            colours = [(v - vmin + 1) / (vmax - vmin + 1) for v in values[variable]]

            message = f"{variable}: {data:.1f} {unit[variable]}"

            # Fundalul
            draw.rectangle((0, 0, WIDTH, HEIGHT), (255, 255, 255))

            # Dreptunghi alb cu marimea curenta
            graph_top_point = 25

            for i in range(len(colours)):
                # Marimile trecute intr-un heatmap albastru-rosu
                colour = (1.0 - colours[i]) * 0.6
                r, g, b = [int(x * 255.0) for x in colorsys.hsv_to_rgb(colour, 1.0, 1.0)]

                # Dreptunghi de latime 1 de culoarea potrivita pentru valoarea curenta
                draw.rectangle((i, graph_top_point, i + 1, HEIGHT), (r, g, b))

                # Punct negru pentru valoarea curenta
                line_y = HEIGHT - (colours[i] * (HEIGHT-graph_top_point))
                draw.rectangle((i, line_y, i + 1, line_y + 1), (0, 0, 0))

            # Afisarea in text a marimii si valorii curente
            draw.text((0, 0), message, font=font, fill=(0, 0, 0))

            disp.display(img)

    except KeyboardInterrupt:
        print("SPI loop stops...")
        logger.debug("SPI loop stops...\n")
