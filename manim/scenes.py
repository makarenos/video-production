from manim import *

class SimpleFormula(Scene):
    """Простая сцена с формулой для тестирования"""
    
    def construct(self):
        # Создаем простую формулу
        formula = MathTex(r"E = mc^2")
        formula.scale(2)
        
        # Анимация появления
        self.play(Write(formula), run_time=2)
        self.wait(1)
        
        # Подсветка
        self.play(formula.animate.set_color(BLUE))
        self.wait(1)
        
        # Финал
        self.play(FadeOut(formula))


class TitleCard(Scene):
    """Заглавная карточка"""
    
    def construct(self):
        title = Text("Тестовое видео", font_size=72)
        subtitle = Text("Автоматизация видеопродакшна", font_size=36)
        subtitle.next_to(title, DOWN)
        
        self.play(FadeIn(title), run_time=1)
        self.play(FadeIn(subtitle), run_time=1)
        self.wait(2)
        
        
class OutroCard(Scene):
    """Финальная карточка"""
    
    def construct(self):
        text = Text("Спасибо за просмотр!", font_size=72)
        self.play(Write(text), run_time=2)
        self.wait(2)
