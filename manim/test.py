from manim import *

class ClientServerScene(Scene):
    def construct(self):
        client = Rectangle(width=2, height=1, fill_color=BLUE, fill_opacity=0.5)
        client.to_edge(LEFT)
        client_text = Text("Client", font_size=24).move_to(client.get_center())

        server = Rectangle(width=2, height=1, fill_color=RED, fill_opacity=0.5)
        server.to_edge(RIGHT)
        server_text = Text("Server", font_size=24).move_to(server.get_center())

        self.play(FadeIn(client), FadeIn(client_text))
        self.play(FadeIn(server), FadeIn(server_text))

        request = Text("Request", font_size=18).next_to(client, RIGHT)
        arrow1 = Arrow(start=client.get_right(), end=server.get_left())

        self.play(FadeIn(request))
        self.play(Create(arrow1), request.animate.move_to(arrow1.get_center()))
        self.wait() 
        self.play(FadeOut(request), FadeOut(arrow1))

        response = Text("Response", font_size=18).next_to(server, LEFT)
        arrow2 = Arrow(start=server.get_left(), end=client.get_right())

        self.play(FadeIn(response))
        self.play(Create(arrow2), response.animate.move_to(arrow2.get_center()))
        self.wait()
        self.play(FadeOut(response), FadeOut(arrow2))

        self.wait()
