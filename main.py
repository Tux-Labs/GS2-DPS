"""
FIAP - Engenharia de Software - 1o ano / 2o semestre

Global Solution 2026.2

Differentiated Problem Solving (Matematica / Calculo)

Projeto: CitizenTech para enchentes em Sao Paulo

INTEGRANTES:

1. Nome: Eduardo de Abreu Gouvea        RM: 573414
2. Nome: Felipe Roberto Cassiano       RM: 569238
3. Nome: Paulo Henrique Moreira Angueira RM: 573245
4. Nome: Vinicius Mansur Magalhaes     RM: 571518

Objetivo:

Modelar a intensidade de uma chuva a partir do total diario P (mm)
e da duracao T (horas com chuva), usando funcao, derivada, integral e limite.

Versao adaptada para interface grafica com Tkinter.
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import requests
except ImportError:
    requests = None

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_DISPONIVEL = True
except ImportError:
    MATPLOTLIB_DISPONIVEL = False


NIVEIS = ["Normal", "Atencao", "Alerta", "Emergencia"]
CORTE_INTENSIDADE = 20.0  # hipotese didatica do grupo, em mm/h


def intensidade(x, p, t):
    """Intensidade da chuva em mm/h no instante x."""
    return (6 * p * x * (t - x)) / (t ** 3)


def derivada_intensidade(x, p, t):
    """Derivada de i(x): mostra se a intensidade cresce ou diminui."""
    return (6 * p * (t - 2 * x)) / (t ** 3)


def acumulado(x, p, t):
    """Integral de i(x) de 0 ate x: chuva acumulada em mm."""
    return (6 * p / (t ** 3)) * ((t * x ** 2) / 2 - (x ** 3) / 3)


def calcular_pico(p, t):
    """Pico ocorre quando a derivada e zero: x = T/2."""
    x_pico = t / 2
    i_pico = 1.5 * p / t
    return x_pico, i_pico


def classificar_total(p):
    """Faixas didaticas usadas pelo projeto, nao oficiais do CGE."""
    if p < 20:
        return 0
    elif p < 40:
        return 1
    elif p < 70:
        return 2
    else:
        return 3


def ajustar_por_intensidade(indice_nivel, pico):
    """Se o pico passar de 20 mm/h, sobe um nivel, limitado a Emergencia."""
    if pico > CORTE_INTENSIDADE and indice_nivel < 3:
        return indice_nivel + 1
    return indice_nivel


def intervalo_acima_do_corte(p, t):
    """Retorna o intervalo em que i(x) > 20 mm/h, quando existir."""
    if p <= 0 or t <= 0:
        return None

    x_pico, pico = calcular_pico(p, t)

    if pico <= CORTE_INTENSIDADE:
        return None

    c = CORTE_INTENSIDADE * (t ** 3) / (6 * p)
    delta = (t ** 2) - 4 * c

    if delta <= 0:
        return None

    x1 = (t - math.sqrt(delta)) / 2
    x2 = (t + math.sqrt(delta)) / 2

    return x1, x2


def buscar_open_meteo(data, latitude=-23.5505, longitude=-46.6333):
    """Busca precipitation_sum e precipitation_hours no historico Open-Meteo."""
    if requests is None:
        raise RuntimeError(
            "A biblioteca requests nao esta instalada.\n"
            "Instale com: pip install requests"
        )

    url = "https://archive-api.open-meteo.com/v1/archive"

    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": data,
        "end_date": data,
        "daily": "precipitation_sum,precipitation_hours",
        "timezone": "America/Sao_Paulo"
    }

    resposta = requests.get(url, params=parametros, timeout=15)
    resposta.raise_for_status()

    dados = resposta.json()

    p = dados["daily"]["precipitation_sum"][0]
    t = dados["daily"]["precipitation_hours"][0]

    if p is None or t is None:
        raise ValueError("A API nao retornou dados de chuva para essa data.")

    return float(p), float(t)


class AplicacaoEnchentes:
    def __init__(self, root):
        self.root = root
        self.root.title("CitizenTech - Modelo Matematico de Risco de Enchentes")
        self.root.geometry("1200x760")
        self.root.minsize(1050, 680)

        self.criar_interface()

    def criar_interface(self):
        titulo = tk.Label(
            self.root,
            text="CitizenTech - Modelo Matematico de Risco de Enchentes",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=(12, 4))

        subtitulo = tk.Label(
            self.root,
            text="Differentiated Problem Solving - Global Solution 2026.2",
            font=("Arial", 11)
        )
        subtitulo.pack(pady=(0, 10))

        conteudo = ttk.Frame(self.root, padding=10)
        conteudo.pack(fill="both", expand=True)

        conteudo.columnconfigure(0, weight=1)
        conteudo.columnconfigure(1, weight=2)
        conteudo.rowconfigure(0, weight=1)

        # ---------------- PAINEL ESQUERDO ----------------
        painel_esquerdo = ttk.Frame(conteudo)
        painel_esquerdo.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Entrada manual
        quadro_manual = ttk.LabelFrame(
            painel_esquerdo,
            text="Entrada manual",
            padding=10
        )
        quadro_manual.pack(fill="x", pady=(0, 10))

        ttk.Label(quadro_manual, text="Total de chuva P (mm):").grid(
            row=0, column=0, sticky="w", pady=4
        )

        self.entrada_p = ttk.Entry(quadro_manual, width=18)
        self.entrada_p.grid(row=0, column=1, padx=8, pady=4)

        ttk.Label(quadro_manual, text="Duracao T (horas):").grid(
            row=1, column=0, sticky="w", pady=4
        )

        self.entrada_t = ttk.Entry(quadro_manual, width=18)
        self.entrada_t.grid(row=1, column=1, padx=8, pady=4)

        botao_calcular = ttk.Button(
            quadro_manual,
            text="Calcular",
            command=self.calcular_manual
        )
        botao_calcular.grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(8, 2)
        )

        # Exemplo
        quadro_exemplo = ttk.LabelFrame(
            painel_esquerdo,
            text="Exemplo didatico",
            padding=10
        )
        quadro_exemplo.pack(fill="x", pady=(0, 10))

        ttk.Label(
            quadro_exemplo,
            text="Exemplo do relatorio: 60 mm em 4 horas."
        ).pack(anchor="w", pady=(0, 8))

        ttk.Button(
            quadro_exemplo,
            text="Executar exemplo 60 mm / 4 h",
            command=self.executar_exemplo
        ).pack(fill="x")

        # Open-Meteo
        quadro_api = ttk.LabelFrame(
            painel_esquerdo,
            text="Historico Open-Meteo",
            padding=10
        )
        quadro_api.pack(fill="x", pady=(0, 10))

        ttk.Label(
            quadro_api,
            text="Data (AAAA-MM-DD):"
        ).pack(anchor="w")

        self.entrada_data = ttk.Entry(quadro_api)
        self.entrada_data.pack(fill="x", pady=5)
        self.entrada_data.insert(0, "2026-10-14")

        ttk.Button(
            quadro_api,
            text="Consultar Open-Meteo",
            command=self.consultar_api
        ).pack(fill="x")

        # Nivel de risco
        quadro_nivel = ttk.LabelFrame(
            painel_esquerdo,
            text="Nivel calculado",
            padding=10
        )
        quadro_nivel.pack(fill="x", pady=(0, 10))

        self.label_nivel = tk.Label(
            quadro_nivel,
            text="Aguardando calculo",
            font=("Arial", 15, "bold"),
            bg="#e5e7eb",
            fg="#111827",
            padx=10,
            pady=10
        )
        self.label_nivel.pack(fill="x")

        # Botoes auxiliares
        quadro_botoes = ttk.Frame(painel_esquerdo)
        quadro_botoes.pack(fill="x")

        ttk.Button(
            quadro_botoes,
            text="Limpar",
            command=self.limpar
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ttk.Button(
            quadro_botoes,
            text="Sair",
            command=self.root.destroy
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

        # ---------------- PAINEL DIREITO ----------------
        painel_direito = ttk.Frame(conteudo)
        painel_direito.grid(row=0, column=1, sticky="nsew")

        painel_direito.rowconfigure(0, weight=1)
        painel_direito.rowconfigure(1, weight=1)
        painel_direito.columnconfigure(0, weight=1)

        # Resultados
        quadro_resultados = ttk.LabelFrame(
            painel_direito,
            text="Resultados",
            padding=8
        )
        quadro_resultados.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

        self.texto_resultados = tk.Text(
            quadro_resultados,
            height=16,
            font=("Consolas", 10),
            wrap="word"
        )
        self.texto_resultados.pack(side="left", fill="both", expand=True)

        barra = ttk.Scrollbar(
            quadro_resultados,
            orient="vertical",
            command=self.texto_resultados.yview
        )
        barra.pack(side="right", fill="y")

        self.texto_resultados.configure(yscrollcommand=barra.set)

        # Graficos
        quadro_graficos = ttk.LabelFrame(
            painel_direito,
            text="Graficos",
            padding=8
        )
        quadro_graficos.grid(row=1, column=0, sticky="nsew")

        if MATPLOTLIB_DISPONIVEL:
            self.abas = ttk.Notebook(quadro_graficos)
            self.abas.pack(fill="both", expand=True)

            self.aba_intensidade = ttk.Frame(self.abas)
            self.aba_acumulado = ttk.Frame(self.abas)

            self.abas.add(self.aba_intensidade, text="Intensidade")
            self.abas.add(self.aba_acumulado, text="Acumulado")

            self.fig_intensidade = Figure(figsize=(6, 3.2), dpi=100)
            self.ax_intensidade = self.fig_intensidade.add_subplot(111)

            self.canvas_intensidade = FigureCanvasTkAgg(
                self.fig_intensidade,
                master=self.aba_intensidade
            )
            self.canvas_intensidade.get_tk_widget().pack(
                fill="both",
                expand=True
            )

            self.fig_acumulado = Figure(figsize=(6, 3.2), dpi=100)
            self.ax_acumulado = self.fig_acumulado.add_subplot(111)

            self.canvas_acumulado = FigureCanvasTkAgg(
                self.fig_acumulado,
                master=self.aba_acumulado
            )
            self.canvas_acumulado.get_tk_widget().pack(
                fill="both",
                expand=True
            )
        else:
            ttk.Label(
                quadro_graficos,
                text=(
                    "Matplotlib nao esta instalado.\n"
                    "Os calculos funcionam normalmente, mas os graficos nao serao exibidos.\n\n"
                    "Para instalar: pip install matplotlib"
                ),
                justify="center"
            ).pack(expand=True)

    def calcular_manual(self):
        try:
            p = float(self.entrada_p.get().replace(",", "."))
            t = float(self.entrada_t.get().replace(",", "."))
            self.mostrar_resultados(p, t, "Entrada manual")
        except ValueError:
            messagebox.showerror(
                "Erro",
                "Digite apenas valores numericos para P e T."
            )

    def executar_exemplo(self):
        self.entrada_p.delete(0, tk.END)
        self.entrada_t.delete(0, tk.END)

        self.entrada_p.insert(0, "60")
        self.entrada_t.insert(0, "4")

        self.mostrar_resultados(
            60.0,
            4.0,
            "Exemplo didatico do relatorio"
        )

    def consultar_api(self):
        data = self.entrada_data.get().strip()

        if not data:
            messagebox.showwarning(
                "Atencao",
                "Informe uma data no formato AAAA-MM-DD."
            )
            return

        try:
            p, t = buscar_open_meteo(data)

            if t <= 0:
                messagebox.showwarning(
                    "Sem chuva",
                    "A API retornou 0 horas com chuva. O modelo exige T > 0."
                )
                return

            self.entrada_p.delete(0, tk.END)
            self.entrada_t.delete(0, tk.END)

            self.entrada_p.insert(0, f"{p:.2f}")
            self.entrada_t.insert(0, f"{t:.2f}")

            self.mostrar_resultados(
                p,
                t,
                "Open-Meteo Historical Weather API"
            )

        except Exception as erro:
            messagebox.showerror(
                "Erro na consulta",
                f"Nao foi possivel consultar a API.\n\n{erro}"
            )

    def mostrar_resultados(self, p, t, origem):
        if p < 0 or t <= 0:
            messagebox.showerror(
                "Valores invalidos",
                "P deve ser maior ou igual a 0 e T deve ser maior que 0."
            )
            return

        x_pico, pico = calcular_pico(p, t)

        nivel_inicial = classificar_total(p)
        nivel_final = ajustar_por_intensidade(nivel_inicial, pico)

        derivada_no_pico = derivada_intensidade(x_pico, p, t)
        integral_total = acumulado(t, p, t)

        intervalo = intervalo_acima_do_corte(p, t)

        texto = ""
        texto += "--- RESULTADOS ---\n\n"
        texto += f"Origem dos dados: {origem}\n"
        texto += f"P = {p:.2f} mm\n"
        texto += f"T = {t:.2f} h\n\n"

        texto += "Modelo:\n"
        texto += "i(x) = 6P*x*(T-x) / T^3\n\n"

        texto += f"Pico em x = T/2 = {x_pico:.2f} h\n"
        texto += f"Intensidade maxima = {pico:.2f} mm/h\n"
        texto += f"Derivada no pico = {derivada_no_pico:.2f}\n"
        texto += f"Integral de 0 a T = {integral_total:.2f} mm\n\n"

        texto += "Interpretacao do limite:\n"
        texto += "i_max = 1,5 * P / T\n"
        texto += (
            "Mantendo P fixo, quanto menor for T, maior sera o pico de intensidade.\n"
            "Quando T tende a 0, o valor do pico cresce sem limite.\n\n"
        )

        texto += f"Nivel pelo total diario: {NIVEIS[nivel_inicial]}\n"
        texto += f"Nivel apos considerar o pico: {NIVEIS[nivel_final]}\n\n"

        if intervalo:
            x1, x2 = intervalo
            texto += (
                f"i(x) > {CORTE_INTENSIDADE:.0f} mm/h "
                f"entre {x1:.2f} h e {x2:.2f} h.\n"
            )
        else:
            texto += (
                f"O modelo nao ultrapassa "
                f"{CORTE_INTENSIDADE:.0f} mm/h.\n"
            )

        texto += "\nTabela de apoio:\n"
        texto += "x (h) | i(x) mm/h | acumulado mm\n"
        texto += "-" * 37 + "\n"

        for passo in range(5):
            x = t * passo / 4

            texto += (
                f"{x:5.2f} | "
                f"{intensidade(x, p, t):10.2f} | "
                f"{acumulado(x, p, t):11.2f}\n"
            )

        self.texto_resultados.delete("1.0", tk.END)
        self.texto_resultados.insert(tk.END, texto)

        self.atualizar_nivel(nivel_final)

        if MATPLOTLIB_DISPONIVEL:
            self.atualizar_graficos(p, t)

    def atualizar_nivel(self, indice_nivel):
        nivel = NIVEIS[indice_nivel]

        cores = {
            0: ("#22c55e", "#ffffff"),
            1: ("#facc15", "#111827"),
            2: ("#f97316", "#ffffff"),
            3: ("#dc2626", "#ffffff")
        }

        fundo, texto = cores[indice_nivel]

        self.label_nivel.config(
            text=nivel,
            bg=fundo,
            fg=texto
        )

    def atualizar_graficos(self, p, t):
        xs = [t * i / 100 for i in range(101)]

        intensidades = [
            intensidade(x, p, t)
            for x in xs
        ]

        acumulados = [
            acumulado(x, p, t)
            for x in xs
        ]

        x_pico, pico = calcular_pico(p, t)

        # Grafico de intensidade
        self.ax_intensidade.clear()

        self.ax_intensidade.plot(
            xs,
            intensidades,
            label="i(x)"
        )

        self.ax_intensidade.axhline(
            CORTE_INTENSIDADE,
            linestyle="--",
            label="Corte 20 mm/h"
        )

        self.ax_intensidade.scatter(
            [x_pico],
            [pico]
        )

        self.ax_intensidade.set_title(
            "Intensidade modelada da chuva"
        )
        self.ax_intensidade.set_xlabel(
            "Tempo desde o inicio da chuva (h)"
        )
        self.ax_intensidade.set_ylabel(
            "Intensidade (mm/h)"
        )
        self.ax_intensidade.grid(
            True,
            alpha=0.25
        )
        self.ax_intensidade.legend()

        self.fig_intensidade.tight_layout()
        self.canvas_intensidade.draw()

        # Grafico de acumulado
        self.ax_acumulado.clear()

        self.ax_acumulado.plot(
            xs,
            acumulados
        )

        self.ax_acumulado.set_title(
            "Acumulado de chuva pelo modelo"
        )
        self.ax_acumulado.set_xlabel(
            "Tempo desde o inicio da chuva (h)"
        )
        self.ax_acumulado.set_ylabel(
            "Precipitacao acumulada (mm)"
        )
        self.ax_acumulado.grid(
            True,
            alpha=0.25
        )

        self.fig_acumulado.tight_layout()
        self.canvas_acumulado.draw()

    def limpar(self):
        self.entrada_p.delete(0, tk.END)
        self.entrada_t.delete(0, tk.END)

        self.texto_resultados.delete("1.0", tk.END)

        self.label_nivel.config(
            text="Aguardando calculo",
            bg="#e5e7eb",
            fg="#111827"
        )

        if MATPLOTLIB_DISPONIVEL:
            self.ax_intensidade.clear()
            self.ax_acumulado.clear()

            self.canvas_intensidade.draw()
            self.canvas_acumulado.draw()


def main():
    root = tk.Tk()
    app = AplicacaoEnchentes(root)
    root.mainloop()


if __name__ == "__main__":
    main()