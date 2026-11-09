from machine import Pin, PWM, I2C
import neopixel
import time
import random
from machine_i2c_lcd import I2cLcd

# === NeoPixels ===
np_red = neopixel.NeoPixel(Pin(5), 16)
np_green = neopixel.NeoPixel(Pin(18), 16)
np_blue = neopixel.NeoPixel(Pin(19), 16)
# === Buzzer ===
buzzer = PWM(Pin(25), freq=1000, duty=0)

# === Touch Sensors ===
touch_pins = {
    "red": Pin(4, Pin.IN),
    "green": Pin(32, Pin.IN),
    "blue": Pin(33, Pin.IN)
}

# === LCD Setup ===
I2C_ADDR = 0x3f
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
lcd.backlight_on()

# === Start Button on GPIO 27 ===
start_button = Pin(27, Pin.IN, Pin.PULL_UP)

# === Functions ===
def show_color(color):
    strip = {"red": np_red, "green": np_green, "blue": np_blue}[color]
    for i in range(16):
        if color == "red":
            strip[i] = (255, 0, 0)
        elif color == "green":
            strip[i] = (0, 255, 0)
        elif color == "blue":
            strip[i] = (0, 0, 255)
    strip.write()

def turn_off_all():
    for strip in [np_red, np_green, np_blue]:
        for i in range(16):
            strip[i] = (0, 0, 0)
        strip.write()

def beep(freq=1000, duration=100):
    buzzer.freq(freq)
    buzzer.duty(800)
    time.sleep_ms(duration)
    buzzer.duty(0)

def game_over_melody():
    notes = [660, 520, 440, 330, 220, 0]
    durations = [150, 150, 150, 150, 300, 200]
    for note, dur in zip(notes, durations):
        if note > 0:
            buzzer.freq(note)
            buzzer.duty(800)
        else:
            buzzer.duty(0)
        time.sleep_ms(dur)
    buzzer.duty(0)

# === MAIN GAME LOOP ===
while True:
    # === Wait for Button Press ===
    lcd.clear()
    lcd.putstr("Press Button to")
    lcd.move_to(0, 1)
    lcd.putstr("Start Game")

    while start_button.value() == 1:
        time.sleep(0.01)
    while start_button.value() == 0:
        time.sleep(0.01)

    # === Start Game ===
    lcd.clear()
    lcd.putstr("Game Start")
    time.sleep(0.7)

    score = 0
    rounds = 15

    for i in range(rounds):
        lcd.clear()
        target_color = random.choice(["red", "green", "blue"])
        show_color(target_color)

        start_time = time.ticks_ms()
        touched = False

        while time.ticks_diff(time.ticks_ms(), start_time) < 1000:
            for color, pin in touch_pins.items():
                if pin.value() == 1:
                    touched = True
                    lcd.clear()
                    if color == target_color:
                        lcd.putstr("Correct!")
                        beep(1000, 80)
                        score += 1
                    else:
                        lcd.putstr("Wrong!")
                        beep(300, 200)
                    break
            if touched:
                break

        turn_off_all()
        time.sleep(0.3)

    # === End Game ===
    lcd.clear()
    lcd.putstr("Game Over")
    time.sleep(0.5)
    lcd.clear()
    lcd.putstr("Score: {}/{}".format(score, rounds))
    game_over_melody()
    time.sleep(5)
    lcd.clear()


