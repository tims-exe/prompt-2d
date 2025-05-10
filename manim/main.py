from manim import *

class HelloWorld(Scene):
    def construct(self):
        circle = Circle(color=WHITE, fill_opacity=0).scale(1)
        text = Text("Hello World", font_size=72, color=WHITE)
        text.move_to(ORIGIN)
        self.add(circle)
        self.play(circle.animate.set_width(10), run_time=5)
        self.play(FadeIn(text, run_time=1))

