import sys
import tkinter as tk
import customtkinter as cctk
from threading import Thread
import queue
import builtins
import time
import os
import re
import ctypes

# Ajustar o path para poder importar o TCC
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TCC.pipeline import rodar_pipeline


class GUI_Terminal(cctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("DB Reader")
        self.geometry("450x500")
        self.resizable(False, False)
        cctk.set_appearance_mode("dark")

        # Regex para remover códigos ANSI
        self.ansi_escape = re.compile(
            r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
        )

        # Configuração de layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Caixa de texto
        self.textbox = cctk.CTkTextbox(
            self,
            font=("Consolas", 13),
            text_color="#cccccc",
            fg_color="#1e1e1e"
        )

        self.textbox.grid(
            row=0,
            column=0,
            padx=10,
            pady=(10, 5),
            sticky="nsew"
        )

        self.textbox.tag_config(
            "red",
            foreground="#ff4d4d"
        )

        self.textbox.tag_config(
            "green",
            foreground="#4ade80"
        )

        self.textbox.configure(state="disabled")

        # Frame de entrada
        self.input_frame = cctk.CTkFrame(
            self,
            fg_color="#1e1e1e"
        )

        self.input_frame.grid(
            row=1,
            column=0,
            padx=10,
            pady=(5, 10),
            sticky="ew"
        )

        self.input_frame.grid_columnconfigure(1, weight=1)

        # >
        self.prompt_label = cctk.CTkLabel(
            self.input_frame,
            text=">",
            font=("Consolas", 14, "bold"),
            text_color="#007acc"
        )

        self.prompt_label.grid(
            row=0,
            column=0,
            padx=(5, 5)
        )

        # Campo de entrada
        self.entry = cctk.CTkEntry(
            self.input_frame,
            placeholder_text="Digite aqui...",
            font=("Consolas", 13),
            fg_color="#3c3c3c",
            border_color="#3c3c3c",
            text_color="#ffffff"
        )

        self.entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 5),
            pady=5
        )

        self.entry.bind(
            "<Return>",
            lambda e: self.processar_entrada()
        )

        # Botão Buscar
        self.btn_buscar = cctk.CTkButton(
            self.input_frame,
            text="Buscar",
            width=60,
            command=self.processar_entrada,
            fg_color="#4a4a4a",
            hover_color="#5a5a5a"
        )

        self.btn_buscar.grid(
            row=0,
            column=2,
            padx=2,
            pady=5
        )

        # Botão Cancelar
        self.btn_cancelar = cctk.CTkButton(
            self.input_frame,
            text="Cancelar",
            width=60,
            command=self.cancelar_comando,
            fg_color="#a1260d",
            hover_color="#801e0a"
        )

        self.btn_cancelar.grid(
            row=0,
            column=3,
            padx=(2, 5),
            pady=5
        )

        # Filas
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()

        # Redirecionar stdout e stderr
        sys.stdout = self.StdoutRedirector(
            self.output_queue,
            self
        )

        sys.stderr = self.StdoutRedirector(
            self.output_queue,
            self
        )

        # Substituir input()
        builtins.input = self.custom_input

        # Atualização da interface
        self.after(
            100,
            self.update_textbox
        )

        # Variáveis da animação
        self.is_thinking = False
        self.thinking_start_time = 0
        self.thinking_dots = 0
        self.thinking_line_index = None

        # Mantido para compatibilidade
        self.waiting_for_insight = False

        # Iniciar worker
        self.iniciar_worker()

    # ---------------------------------------------------------
    # WORKER
    # ---------------------------------------------------------

    def iniciar_worker(self):

        self.worker_thread = Thread(
            target=self.run_pipeline_loop,
            daemon=True
        )

        self.worker_thread.start()

        self.after(
            500,
            self.animate_thinking
        )

    # ---------------------------------------------------------
    # ANIMAÇÃO
    # ---------------------------------------------------------

    def animate_thinking(self):

        if self.is_thinking:

            elapsed = time.time() - self.thinking_start_time

            if elapsed >= 3.0:

                self.thinking_dots = (
                    self.thinking_dots % 3
                ) + 1

                dots_str = "." * self.thinking_dots

                self.textbox.configure(
                    state="normal"
                )

                if self.thinking_line_index:

                    try:

                        self.textbox.delete(
                            f"{self.thinking_line_index} linestart",
                            f"{self.thinking_line_index} lineend"
                        )

                        self.textbox.insert(
                            self.thinking_line_index,
                            dots_str
                        )

                    except Exception:
                        pass

                else:

                    self.textbox.insert(
                        tk.END,
                        "\n" + dots_str
                    )

                    self.thinking_line_index = (
                        self.textbox.index(
                            "end-1c linestart"
                        )
                    )

                self.textbox.see(tk.END)

                self.textbox.configure(
                    state="disabled"
                )

        else:

            if self.thinking_line_index:

                self.textbox.configure(
                    state="normal"
                )

                try:

                    self.textbox.delete(
                        f"{self.thinking_line_index} linestart",
                        f"{self.thinking_line_index} lineend+1c"
                    )

                except Exception:
                    pass

                self.thinking_line_index = None

                self.textbox.configure(
                    state="disabled"
                )

        self.after(
            500,
            self.animate_thinking
        )

    # ---------------------------------------------------------
    # REDIRECIONADOR
    # ---------------------------------------------------------

    class StdoutRedirector:

        def __init__(self, q, parent):
            self.q = q
            self.parent = parent

        def write(self, text):

            if text.strip():
                self.parent.is_thinking = False

            self.q.put(text)

        def flush(self):
            pass

    # ---------------------------------------------------------
    # ANSI
    # ---------------------------------------------------------

    def strip_ansi(self, text):
        return self.ansi_escape.sub('', text)

    # ---------------------------------------------------------
    # INPUT
    # ---------------------------------------------------------

    def custom_input(self, prompt=""):

        self.is_thinking = False

        if prompt:

            clean_prompt = self.strip_ansi(prompt)

            # O "Você:" já é mostrado por processar_entrada()
            if "Você:" not in clean_prompt:

                self.output_queue.put(
                    clean_prompt
                )

        # Habilitar entrada
        self.after(
            0,
            lambda: self.entry.configure(
                state="normal"
            )
        )

        self.after(
            0,
            lambda: self.btn_buscar.configure(
                state="normal"
            )
        )

        self.after(
            0,
            lambda: self.entry.focus_set()
        )

        # Esperar resposta
        while True:

            try:

                valor = self.input_queue.get(
                    timeout=0.1
                )

                self.thinking_start_time = time.time()
                self.is_thinking = True

                return valor

            except queue.Empty:

                continue

    # ---------------------------------------------------------
    # PROCESSAR ENTRADA
    # ---------------------------------------------------------

    def processar_entrada(self):

        texto = self.entry.get()

        if not texto.strip():
            return

        # Comando CLEAR
        if texto.strip().lower() == "clear":

            self.textbox.configure(
                state="normal"
            )

            self.textbox.delete(
                "1.0",
                tk.END
            )

            self.textbox.configure(
                state="disabled"
            )

            self.entry.delete(
                0,
                tk.END
            )

            return

        # Limpar entrada
        self.entry.delete(
            0,
            tk.END
        )

        # Bloquear enquanto processa
        self.entry.configure(
            state="disabled"
        )

        self.btn_buscar.configure(
            state="disabled"
        )

        # Mostrar pergunta
        self.output_queue.put(
            f"\nVocê: {texto}\n"
        )

        # Enviar resposta para input()
        self.input_queue.put(
            texto
        )

        self.thinking_start_time = time.time()
        self.is_thinking = True

    # ---------------------------------------------------------
    # CANCELAR
    # ---------------------------------------------------------

    def cancelar_comando(self):

        self.is_thinking = False

        self.output_queue.put(
            "\nBusca interrompida pelo usuário!\n"
        )

        if self.worker_thread.is_alive():

            thread_id = self.worker_thread.ident

            try:

                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread_id),
                    ctypes.py_object(KeyboardInterrupt)
                )

                if res > 1:

                    ctypes.pythonapi.PyThreadState_SetAsyncExc(
                        ctypes.c_long(thread_id),
                        None
                    )

            except Exception:
                pass

        # Limpar fila
        while not self.input_queue.empty():

            try:
                self.input_queue.get_nowait()
            except queue.Empty:
                break

        # Reabilitar entrada
        self.after(
            0,
            lambda: self.entry.configure(
                state="normal"
            )
        )

        self.after(
            0,
            lambda: self.btn_buscar.configure(
                state="normal"
            )
        )

    # ---------------------------------------------------------
    # ATUALIZAR TEXTBOX
    # ---------------------------------------------------------

    def update_textbox(self):

        while not self.output_queue.empty():

            msg = self.output_queue.get()

            clean_msg = self.strip_ansi(
                msg
            )

            self.textbox.configure(
                state="normal"
            )

            # Remover pontinhos
            if (
                self.thinking_line_index
                and clean_msg.strip()
            ):

                try:

                    self.textbox.delete(
                        f"{self.thinking_line_index} linestart -1c",
                        f"{self.thinking_line_index} lineend"
                    )

                except Exception:

                    try:

                        self.textbox.delete(
                            f"{self.thinking_line_index} linestart",
                            f"{self.thinking_line_index} lineend+1c"
                        )

                    except Exception:
                        pass

                self.thinking_line_index = None

            # ERROS
            if any(
                x in clean_msg
                for x in [
                    "INVALID",
                    "Resultado inválido ou não encontrado!",
                    "Erro técnico:",
                    "Busca interrompida pelo usuário!",
                    "Erro no loop:"
                ]
            ):

                self.textbox.insert(
                    tk.END,
                    clean_msg,
                    "red"
                )

                self.is_thinking = False

            # PERGUNTAS S/N
            elif any(
                x in clean_msg
                for x in [
                    "Gerar gráfico?",
                    "Exportar CSV?"
                ]
            ):

                self.textbox.insert(
                    tk.END,
                    clean_msg,
                    "green"
                )

                self.is_thinking = False

            # RESPOSTA NORMAL
            else:

                self.textbox.insert(
                    tk.END,
                    clean_msg
                )

            self.textbox.see(tk.END)

            self.textbox.configure(
                state="disabled"
            )

        self.after(
            100,
            self.update_textbox
        )

    # ---------------------------------------------------------
    # LOOP PRINCIPAL
    # ---------------------------------------------------------

    def run_pipeline_loop(self):

        while True:

            try:

                pergunta = input(
                    "\nVocê: "
                )

                # O pipeline já controla:
                # resposta
                # gráfico
                # CSV
                #
                # Portanto NÃO fazemos print() aqui.
                rodar_pipeline(
                    pergunta
                )

            except KeyboardInterrupt:

                time.sleep(0.5)

            except Exception as e:

                print(
                    f"\nErro no loop: {e}"
                )

                time.sleep(1)


if __name__ == "__main__":

    app = GUI_Terminal()
    app.mainloop()