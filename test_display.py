
import ST7735
from PIL import Image, ImageDraw, ImageFont
from time import sleep

# Create LCD class instance.

"""Create an instance of the display using SPI communication.

        Must provide the GPIO pin number for the D/C pin and the SPI driver.

        Can optionally provide the GPIO pin number for the reset pin as the rst parameter.

        :param port: SPI port number
        :param cs: SPI chip-select number (0 or 1 for BCM)
        :param backlight: Pin for controlling backlight
        :param rst: Reset pin for ST7735
        :param width: Width of display connected to ST7735
        :param height: Height of display connected to ST7735
        :param rotation: Rotation of display connected to ST7735
        :param offset_left: COL offset in ST7735 memory
        :param offset_top: ROW offset in ST7735 memory
        :param invert: Invert display
        :param spi_speed_hz: SPI speed (in Hz)

"""
disp = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)
font_size = 30
font = ImageFont.truetype("ttf/Signature.ttf", font_size)
text_colour = (255, 255, 255)
back_colour = (0, 170, 0)

Done = False


# Width and height to calculate text position.
WIDTH = disp.width
HEIGHT = disp.height


# New canvas to draw on.
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

Pic = Image.open("color.jpg")
Scale = 1.0
Wscale = Pic.width / WIDTH
Hscale = Pic.height / HEIGHT
if Wscale > Hscale: 
	Scale = Wscale
else:
	Scale = Hscale
Pwidth = int(Pic.width/Wscale)
Pheight= int(Pic.height/Hscale)
SPic = Pic.resize((Pwidth,Pheight))

Px = int((WIDTH -Pwidth)/2)
Py = int((HEIGHT -Pheight)/2)
while not Done:
	try:
		# draw.rectangle((0, 0, 160, 80), back_colour)
		# img.paste(SPic,(Px,Py))
		# disp.display(img)
		# sleep(5.0)


		
		message = "  Hi there! Reviewing the Enviro+ ..."
		size_x, size_y = draw.textsize(message, font)
		# Calculate Y text position to center it 
		y = (HEIGHT / 2) - (size_y / 2)
		for c in message:
			# Draw background rectangle and write text.
			draw.rectangle((0, 0, 160, 80), back_colour)
			draw.text((0, y), message, font=font, fill=text_colour)
			disp.display(img)   # :param image: Should be RGB format and the same dimensions as the display hardware. 
			message  = message[1::]+message[0]
			sleep(0.1)
	except KeyboardInterrupt:
		disp.set_backlight(0)
		quit()