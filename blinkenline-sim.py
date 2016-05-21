#!/usr/bin/env python2

import socket
from argparse import ArgumentParser
from select import poll, POLLIN

import pygame

if __name__ == "__main__":
    aparse = ArgumentParser(description="BlinkenLine Simulator")
    aparse.add_argument("leds", type=int, metavar="LEDs",
                        help="Number of LEDs")

    aparse.add_argument("--host", type=str, metavar="HOST",
                        help="address on which to listen",
                        default="127.0.0.1", required=False)

    aparse.add_argument("--port", type=int, metavar="PORT",
                        help="port on which to listen",
                        default=2342, required=False)

    aparse.add_argument("--switchrg",
                        action="store_const", const=True,
                        required=False)

    args = aparse.parse_args()

    # socket stuff
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 8888))
    sock.setblocking(0)

    sockpoll = poll()
    sockpoll.register(sock, POLLIN)

    # logic stuff
    switchrg = args.switchrg #On some WS2812 LED stripes, R and G Channels are switched
    leds = args.leds
    buffer = []

    # pygame stuff
    clock = pygame.time.Clock()

    pygame.display.init()
    # screen init: we need 10px width per LED
    screen = pygame.display.set_mode((leds*10, 100))

    shutdown = False

    for i in range(leds):
        buffer.append((255,255,255))

    while not shutdown:
        clock.tick(30)

        # get data
        event_socks = sockpoll.poll(20)

        data = None

        # did we receive data?
        if len(event_socks) > 0 and event_socks[0][1] & POLLIN:
            data, _ = sock.recvfrom(3*leds)

            buffer_index = 0

            # process data
            for i in xrange(0, len(data), 3):
                # a chunk consists of one to three bytes
                chunk = data[i:i+3]
                # default for new color is black
                new_color = [0,0,0]
                for j, byte in zip(range(len(chunk)), chunk):
                    # pygame wants integers for colors, so we convert

                    if not switchrg:
                        new_color[j] = ord(chunk[j])
                    else:
                        if j==1:
                            new_color[2] = ord(chunk[1])
                        elif j==2:
                            new_color[1] = ord(chunk[2]) 
                        elif j==3:
                            new_color[3] = ord(chunk[3])

                # LED color values are tuples, because semantics
                buffer[buffer_index] = tuple(new_color)
                buffer_index += 1

        # render
        for i, led in zip(range(len(buffer)), buffer):
            pygame.draw.circle(screen, led, (i*10-5, 5), 5)

        pygame.display.update()

        # process quit event
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit() # deinit pygame
                shutdown = True 
