#! /usr/bin/env python

import curses
import curses.ascii
import locale
import sys
import time

class Screen(object):
    def __enter__(self):
        self.scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.scr.keypad(1)

        return self.scr

    def __exit__(self, type_, value, traceback):
        self.scr.keypad(0)
        curses.curs_set(0)
        curses.nocbreak()
        curses.echo()

        curses.endwin()

class TUI(object):
    commands = {
        'q': lambda _: sys.exit(0),
    }

    bindings = {
        'j': lambda self: self.do_next_row(),
        'k': lambda self: self.do_previous_row(),
        ':': lambda self: self.do_colon(),
        'C-g': lambda self: self.do_info(),
    }

    def __init__(self):
        def raw(k):
            if k.startswith('C-'):
                k = curses.ascii.ctrl(k[2:])

            return ord(k)

        raw_bindings = {}
        for k, b in self.bindings.items():
            raw_bindings[raw(k)] = b

        self.bindings = raw_bindings

        self.row = 1
        self.column = 1

    def do_previous_row(self):
        if self.row > 1:
            self.row -= 1
        self.render()
        self.scr.refresh()

    def do_next_row(self):
        self.row += 1
        self.render()
        self.scr.refresh()

    def do_colon(self):
        cmd = self.run_colon_mode()
        if cmd:
            self.commands.get(cmd, lambda s: self.set_status_line('unknown command %r' % s))(cmd)
        else:
            self.set_status_line('')

    def do_info(self):
        self.set_status_line('%d lines' % self.lines_count())

    def iter_from(self, row):
        for k, v in self.bindings.items():
            yield '%s = %s' % (k, v.__name__)

    def lines_count(self):
        return len(self.bindings)

    def set_status_line(self, s):
        self.status.addstr(0, 0, s)
        self.status.clrtoeol()
        self.status.refresh()

    def render(self):
        for y, row_content in enumerate(self.iter_from(self.row)):
            if  y == self.rows:
                break

            self.scr.addstr(y, 0, row_content)
            self.scr.clrtoeol()

    def run(self):
        with Screen() as scr:
            lines, cols = scr.getmaxyx()

            self.scr = curses.newwin(lines-1, cols, 0, 0)
            self.rows = lines - 1
            self.status = curses.newwin(1, cols, lines-1, 0)

            self.render()
            self.scr.refresh()

            while True:
                self.bindings.get(self.scr.getch(), lambda _: None)(self)

    def run_colon_mode(self):
        s = ''
        while True:
            self.set_status_line(':' + s)

            ch = self.status.getch()

            if ch == 10:
                break

            if ch == ord(curses.ascii.ctrl('G')):
                return None

            s += chr(ch)

        return s

if __name__ == '__main__':
    ui = TUI()
    ui.run()
