import timeit
import time


class GameClock:

    def __init__(self, max_fps):

        self.min_fps = 30
        self.max_fps = max_fps if max_fps > self.min_fps else self.min_fps
        self.fps_cost_time = (1 / self.max_fps)
        self.start = 0
        self.elapsed = 0
        self.delta_time = 0
        self.count_down = 0
        self.fps = self.max_fps

    def tick(self):
        self.elapsed = (timeit.default_timer() - self.start)
        if self.elapsed >= self.fps_cost_time:
            sleep_time = 0
        else:
            sleep_time = self.fps_cost_time - self.elapsed
        if sleep_time > 0:
            GameClock.sleep(sleep_time)
        self.elapsed += sleep_time
        self.delta_time += self.elapsed
        if self.delta_time > 1.0:
            self.delta_time = 0
            self.fps = self.count_down
            self.count_down = 0
        self.count_down += 1
        self.start = timeit.default_timer()
        return self.elapsed

    def get_fps(self):
        return self.fps

    @staticmethod
    def sleep(delay_time):
        finish = time.perf_counter() + delay_time
        while time.perf_counter() < finish:
            pass
