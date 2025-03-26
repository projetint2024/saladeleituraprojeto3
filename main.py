import requests
from datetime import datetime, timezone
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from kivy.uix.image import Image

class MyApp(App):
    def build(self):
        return Image(source='logo.jpg')



# URL da API
API_URL = "https://projetoint.pythonanywhere.com/alerta/app"

class ListaAtrasos(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [10, 10, 10, 10]
        self.spacing = 10
        self.size_hint = (1, 1)

        # Definir o fundo claro
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Cor clara (bege claro)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Título do app
        self.add_widget(Label(text="Livros em Atraso", font_size=64, bold=True, color=(0, 0, 0, 1), size_hint=(1, None), height=100))
        
       

        # Adicionando uma área rolável para a lista de atrasos
        scrollview = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        self.container = BoxLayout(orientation="vertical", size_hint_y=None)
        scrollview.add_widget(self.container)
        self.add_widget(scrollview)

        # Atualizar os dados imediatamente e agendar atualizações a cada X segundos
        self.atualizar_dados()
        Clock.schedule_interval(lambda dt: self.atualizar_dados(), 30)

    def _update_rect(self, *args):
        """Atualiza o tamanho e a posição do fundo."""
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def atualizar_dados(self):
        registros = self.buscar_dados_atrasados()
        self.container.clear_widgets()
        if registros:
            
        
            for registro in registros:
                

                item = BoxLayout(orientation="vertical")
                


                item.add_widget(Label(text=f"Aluno: {registro['nome_aluno']}", font_size=49, bold=True, color=(0, 0, 0, 1)))
                item.add_widget(Label(text=f"Livro: {registro['nome_do_livro']}", font_size=49, color=(0, 0, 0, 1)))
                item.add_widget(Label(text=f"Número do Tombo: {registro['numero_do_tombo']}", font_size=49, color=(0, 0, 0, 1)))
                item.add_widget(Label(text=f"Série: {registro['serie']}", font_size=49, color=(0, 0, 0, 1)))
                item.add_widget(Label(text=f"Data de Devolução: {registro['data_formatada']}", font_size=49, color=(0, 0, 0, 1)))
                item.add_widget(Label(text="--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------", font_size=12, color=(0.7, 0.7, 0.7, 1)))

                self.container.add_widget(item)
            # Ajusta a altura do container dinamicamente
            self.container.size_hint_y = None
            self.container.height = len(registros) * 330  # Altura por item
        else:
            self.container.add_widget(Label(text="Nenhum livro atrasado!", font_size=18, color=(1, 0, 0, 1)))

    def buscar_dados_atrasados(self):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                dados = response.json()
                atrasados = []
                data_atual = datetime.now(timezone.utc)

                for registro in dados:
                    # Tentar converter a data de devolução
                    data_devolucao = datetime.strptime(
                        registro['data_devolucao'], "%a, %d %b %Y %H:%M:%S %Z"
                    ).replace(tzinfo=timezone.utc)

                    if data_devolucao < data_atual and registro['devolvido'] == "n":
                        # Adicionar uma versão formatada da data para exibição
                        registro['data_formatada'] = data_devolucao.strftime("%d/%m/%Y")
                        atrasados.append(registro)

                # Ordenar os registros pela data original de devolução
                atrasados_ordenados = sorted(
                    atrasados, key=lambda x: datetime.strptime(
                        x['data_devolucao'], "%a, %d %b %Y %H:%M:%S %Z"
                    ).replace(tzinfo=timezone.utc), reverse=True
                )
                return atrasados_ordenados
            else:
                print(f"Erro ao acessar API: {response.status_code}")
                return []
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return []



class AlertaApp(App):
    def build(self):
        return ListaAtrasos()

if __name__ == "__main__":
    AlertaApp().run()

