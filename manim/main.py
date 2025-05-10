from manim import *

class CircleToSquare(Scene):
    def construct(self):
        circle = Circle(color=WHITE).shift(LEFT)
        square = Square(side_length=2, color=RED).shift(RIGHT)

        self.play(Create(circle))
        self.play(Transform(circle, square))
        self.play(Transform(square, circle.copy().set_color(WHITE)))
        self.wait()