import sys
import tkinter as tk
import customtkinter as cctk
from threading import Event, Thread
import queue
import builtins
import time
import os
import re


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.pipeline import rodar_pipeline

class GUI_Terminal(cctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("DB Reader")
        self.geometry("450x500")
        self.resizable(False, False)
        cctk.set_appearance_mode("dark")


        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.textbox = cctk.CTkTextbox(
            self,
            font=("Consolas", 13),
            text_color="#cccccc",
            fg_color="#1e1e1e"
        )
        self.textbox.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.textbox.tag_config(
            "red",
            foreground="#ff4d4d"
        )
        self.textbox.tag_config(
            "green",
            foreground="#4ade80"
        )
        self.textbox.configure(state="disabled")


        self.input_frame = cctk.CTkFrame(
            self,
            fg_color="#1e1e1e"
        )
        self.input_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)


        self.prompt_label = cctk.CTkLabel(
            self.input_frame,
            text=">",
            font=("Consolas", 14, "bold"),
            text_color="#007acc"
        )
        self.prompt_label.grid(row=0, column=0, padx=(5, 5))


        self.entry = cctk.CTkEntry(
            self.input_frame,
            placeholder_text="Digite aqui...",
            font=("Consolas", 13),
            fg_color="#3c3c3c",
            border_color="#3c3c3c",
            text_color="#ffffff"
        )
        self.entry.grid(row=0, column=1, sticky="ew", padx=(0, 5), pady=5)
        self.entry.bind("<Return>", lambda e: self.processar_entrada())


        self.btn_buscar = cctk.CTkButton(
            self.input_frame,
            text="Buscar",
            width=60,
            command=self.processar_entrada,
            fg_color="#4a4a4a",
            hover_color="#5a5a5a"
        )
        self.btn_buscar.grid(row=0, column=2, padx=2, pady=5)


        self.btn_cancelar = cctk.CTkButton(
            self.input_frame,
            text="Cancelar",
            width=60,
            command=self.cancelar_comando,
            fg_color="#a1260d",
            hover_color="#801e0a"
        )
        self.btn_cancelar.grid(row=0, column=3, padx=(2, 5), pady=5)
        self.cancel_event = Event()
        self.awaiting_choice = False


        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()


        sys.stdout = self.StdoutRedirector(self.output_queue, self)
        sys.stderr = self.StdoutRedirector(self.output_queue, self)


        builtins.input = self.custom_input


        self.after(100, self.update_textbox)


        self.is_thinking = False
        self.thinking_start_time = 0
        self.thinking_dots = 0
        self.thinking_line_index = None


        self.iniciar_worker()


    def iniciar_worker(self):
        self.worker_thread = Thread(target=self.run_pipeline_loop, daemon=True)
        self.worker_thread.start()
        self.after(500, self.animate_thinking)


    def animate_thinking(self):
        if self.is_thinking:
            elapsed = time.time() - self.thinking_start_time
            if elapsed >= 3.0:
                self.thinking_dots = (self.thinking_dots % 3) + 1
                dots_str = "." * self.thinking_dots
                self.textbox.configure(state="normal")
                if self.thinking_line_index:
                    try:
                        self.textbox.delete(
                            f"{self.thinking_line_index} linestart",
                            f"{self.thinking_line_index} lineend"
                        )
                        self.textbox.insert(self.thinking_line_index, dots_str)
                    except Exception:
                        pass
                else:
                    self.textbox.insert(tk.END, "\n" + dots_str)
                    self.thinking_line_index = (self.textbox.index("end-1c linestart"))
                self.textbox.see(tk.END)
                self.textbox.configure(state="disabled")
        else:
            if self.thinking_line_index:
                self.textbox.configure(state="normal")
                try:
                    self.textbox.delete(
                        f"{self.thinking_line_index} linestart",
                        f"{self.thinking_line_index} lineend+1c"
                    )
                except Exception:
                    pass
                self.thinking_line_index = None
                self.textbox.configure(state="disabled")
        self.after(500, self.animate_thinking)


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


    def strip_ansi(self, text):
        return self.ansi_escape.sub('', text)


    def custom_input(self, prompt=""):
        self.is_thinking = False
        if prompt:
            clean_prompt = self.strip_ansi(prompt)


            if "Você:" not in clean_prompt:
                self.output_queue.put(clean_prompt)


        self.after(0, lambda: self.entry.configure(state="normal"))
        self.after(0, lambda: self.btn_buscar.configure(state="normal"))
        self.after(0, lambda: self.entry.focus_set())


        self.awaiting_choice = "Gerar gráfico?" in prompt or "Exportar CSV?" in prompt
        while True:
            try:
                valor = self.input_queue.get(timeout=0.1)
                self.thinking_start_time = time.time()
                self.is_thinking = True
                self.awaiting_choice = False
                return valor
            except queue.Empty:
                continue


    def processar_entrada(self):
        texto = self.entry.get()
        if not texto.strip():
            return


        if texto.strip().lower() == "clear":
            self.textbox.configure(state="normal")
            self.textbox.delete("1.0", tk.END)
            self.textbox.configure(state="disabled")
            self.entry.delete(0, tk.END)
            return


        self.entry.delete(0, tk.END)


        self.entry.configure(state="disabled")
        self.btn_buscar.configure(state="disabled")
        self.cancel_event.clear()


        self.output_queue.put(f"\nVocê: {texto}\n")


        self.input_queue.put(texto)
        self.thinking_start_time = time.time()
        self.is_thinking = True


    def cancelar_comando(self):


        self.cancel_event.set()
        self.is_thinking = False
        self.output_queue.put("\nCancelamento solicitado.\n")

        if self.awaiting_choice and self.input_queue.empty():
            self.input_queue.put("N")


    def update_textbox(self):
        while not self.output_queue.empty():
            msg = self.output_queue.get()
            clean_msg = self.strip_ansi(msg)
            self.textbox.configure(state="normal")


            if (self.thinking_line_index and clean_msg.strip()):
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
                self.textbox.insert(tk.END, clean_msg, "red")
                self.is_thinking = False


            elif any(x in clean_msg for x in ["Gerar gráfico?", "Exportar CSV?"]):
                self.textbox.insert(tk.END, clean_msg, "green")
                self.is_thinking = False


            else:
                self.textbox.insert(tk.END, clean_msg)
            self.textbox.see(tk.END)
            self.textbox.configure(state="disabled")
        self.after(100, self.update_textbox)


    def run_pipeline_loop(self):
        while True:
            try:
                pergunta = input("\nVocê: ")


                rodar_pipeline(pergunta, cancelado=self.cancel_event)
            except KeyboardInterrupt:
                time.sleep(0.5)
            except Exception:
                print("\nNão foi possível concluir a consulta.")
                time.sleep(1)

if __name__ == "__main__":

    app = GUI_Terminal()
    app.mainloop()
