"""
Timer engine — counts down work intervals, detects suppression, fires break alerts.
Uses a single QTimer tick at 1 Hz to stay near-zero CPU.
"""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class TimerEngine(QObject):
    # Emitted when it's time to show the break overlay
    break_due = pyqtSignal()
    # Emitted every second with (elapsed_work_sec, total_work_sec, state)
    tick = pyqtSignal(int, int, str)  # elapsed, total, state

    STATE_WORKING = "working"
    STATE_BREAK = "break"
    STATE_PAUSED = "paused"
    STATE_SUPPRESSED = "suppressed"

    def __init__(self, settings):
        super().__init__()
        self._settings = settings
        self._state = self.STATE_WORKING
        self._elapsed = 0          # seconds since last break/start
        self._break_elapsed = 0    # seconds into current break
        self._suppressed_ticks = 0 # how long we've been suppressed
        self._pending_break = False # break is pending (suppressed)

        self._tray = None
        self._main_window = None

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    def set_tray(self, tray):
        self._tray = tray

    def set_main_window(self, win):
        self._main_window = win

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def reset(self):
        """Reset to start of work interval."""
        self._elapsed = 0
        self._break_elapsed = 0
        self._state = self.STATE_WORKING
        self._pending_break = False

    def skip_break(self):
        """User manually skips the current break."""
        self.reset()

    @property
    def state(self):
        return self._state

    @property
    def elapsed(self):
        return self._elapsed

    def _work_total(self):
        return self._settings.get("work_interval_min", 20) * 60

    def _break_total(self):
        return self._settings.get("break_duration_sec", 20)

    def _tick(self):
        from app.detector import should_suppress_alert

        if self._state == self.STATE_PAUSED:
            self.tick.emit(self._elapsed, self._work_total(), self.STATE_PAUSED)
            return

        if self._state == self.STATE_WORKING:
            self._elapsed += 1
            total = self._work_total()

            if self._elapsed >= total or self._pending_break:
                # Time for a break!
                skip = self._settings.get("skip_fullscreen", True) and should_suppress_alert()
                if skip:
                    self._state = self.STATE_SUPPRESSED
                    self._pending_break = True
                    self._suppressed_ticks += 1
                    self.tick.emit(self._elapsed, total, self.STATE_SUPPRESSED)
                    if self._tray:
                        self._tray.update_tooltip("EyeRest — en attente (fullscreen détecté)")
                    return
                else:
                    self._pending_break = False
                    self._suppressed_ticks = 0
                    self._state = self.STATE_BREAK
                    self._break_elapsed = 0
                    self.break_due.emit()
                    self._show_break()
            else:
                self.tick.emit(self._elapsed, total, self.STATE_WORKING)
                if self._tray:
                    remaining = total - self._elapsed
                    m, s = divmod(remaining, 60)
                    self._tray.update_tooltip(f"EyeRest — prochaine pause dans {m:02d}:{s:02d}")

        elif self._state == self.STATE_SUPPRESSED:
            # Keep checking every second
            skip = self._settings.get("skip_fullscreen", True) and should_suppress_alert()
            if not skip:
                self._state = self.STATE_BREAK
                self._break_elapsed = 0
                self._pending_break = False
                self._suppressed_ticks = 0
                self.break_due.emit()
                self._show_break()
            else:
                self._suppressed_ticks += 1
                self.tick.emit(self._elapsed, self._work_total(), self.STATE_SUPPRESSED)

        elif self._state == self.STATE_BREAK:
            self._break_elapsed += 1
            self.tick.emit(self._break_elapsed, self._break_total(), self.STATE_BREAK)
            if self._break_elapsed >= self._break_total():
                self._state = self.STATE_WORKING
                self._elapsed = 0
                self._break_elapsed = 0
                if self._main_window:
                    self._main_window.hide_break_overlay()
                if self._tray:
                    self._tray.update_tooltip("EyeRest — bonne pause !")

    def _show_break(self):
        if self._main_window:
            self._main_window.show_break_overlay(self._break_total())

    def pause(self):
        self._state = self.STATE_PAUSED

    def resume(self):
        if self._state == self.STATE_PAUSED:
            self._state = self.STATE_WORKING
