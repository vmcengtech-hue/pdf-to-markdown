from __future__ import annotations

import argparse
import os
import queue
import sys
import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "PDF para Markdown"


def convert_pdf(source: Path, ocr_language: str | None, tessdata: str | None, notify) -> Path:
    """Convert one PDF and atomically claim its Markdown destination."""
    source = source.expanduser().resolve(strict=True)
    if not source.is_file() or source.suffix.lower() != ".pdf":
        raise ValueError("Selecione um arquivo PDF válido.")

    notify(("status", "Lendo o PDF e reconhecendo a estrutura…"))
    if tessdata:
        os.environ["TESSDATA_PREFIX"] = tessdata
    import pymupdf
    import pymupdf4llm

    document = pymupdf.open(str(source))
    total = document.page_count
    if total == 0:
        raise ValueError("O PDF não contém páginas.")
    parts: list[str] = []
    try:
        for index in range(total):
            kwargs = {"pages": [index], "page_chunks": True}
            if ocr_language:
                kwargs.update(use_ocr=True, ocr_language=ocr_language)
            chunks = pymupdf4llm.to_markdown(document, **kwargs)
            text = chunks[0].get("text", "") if chunks and isinstance(chunks[0], dict) else ""
            notify(("progress", int((index + 1) * 90 / total)))
            if text.strip():
                parts.append(text.rstrip())
    finally:
        document.close()
    markdown = "\n\n".join(parts).strip() + "\n"
    if not markdown.strip():
        raise ValueError("Não foi possível extrair texto. O PDF pode ser digitalizado; tente habilitar OCR.")

    destination = source.with_suffix(".md")
    notify(("status", "Salvando o Markdown com proteção contra sobrescrita…"))
    notify(("progress", 95))
    # O_EXCL makes the no-overwrite guarantee hold even for simultaneous runs.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(destination, flags, 0o666)
    except FileExistsError:
        raise FileExistsError(f"O arquivo de saída já existe e foi preservado:\n{destination}")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(markdown)
    except Exception:
        try:
            destination.unlink()
        except OSError:
            pass
        raise
    return destination


class ConverterApp:
    def __init__(self, root: tk.Tk, initial_pdf: str | None = None):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("560x330")
        self.root.minsize(500, 300)
        self.root.configure(padx=22, pady=20)
        self.events: queue.Queue = queue.Queue()
        self.busy = False
        self.file_var = tk.StringVar(value=initial_pdf or "")
        self.ocr_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Escolha um arquivo PDF para começar.")
        self.tessdata_var = tk.StringVar(value="")

        ttk.Label(root, text="PDF para Markdown", font=("Segoe UI", 19, "bold")).pack(anchor="w")
        ttk.Label(root, text="Converta documentos no seu computador.", font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 17))

        row = ttk.Frame(root)
        row.pack(fill="x")
        self.path_entry = ttk.Entry(row, textvariable=self.file_var)
        self.path_entry.pack(side="left", fill="x", expand=True)
        self.browse_button = ttk.Button(row, text="Procurar…", command=self.choose_file)
        self.browse_button.pack(side="left", padx=(9, 0))

        ttk.Checkbutton(root, text="Tentar OCR em páginas digitalizadas (requer dados de idioma)", variable=self.ocr_var).pack(anchor="w", pady=(14, 0))
        self.language_var = tk.StringVar(value="por")
        lang = ttk.Frame(root)
        lang.pack(anchor="w", pady=(7, 0))
        ttk.Label(lang, text="Idiomas OCR:").pack(side="left")
        ttk.Entry(lang, textvariable=self.language_var, width=18).pack(side="left", padx=8)
        ttk.Label(lang, text="Ex.: por+eng").pack(side="left")
        data_row = ttk.Frame(root)
        data_row.pack(fill="x", pady=(7, 0))
        ttk.Label(data_row, text="Pasta tessdata:").pack(side="left")
        ttk.Entry(data_row, textvariable=self.tessdata_var).pack(side="left", fill="x", expand=True, padx=8)
        self.tessdata_button = ttk.Button(data_row, text="Localizar…", command=self.choose_tessdata)
        self.tessdata_button.pack(side="left")

        self.progress = ttk.Progressbar(root, mode="indeterminate", maximum=100)
        self.progress.pack(fill="x", pady=(17, 7))
        ttk.Label(root, textvariable=self.status_var, wraplength=510).pack(anchor="w")
        self.convert_button = ttk.Button(root, text="Converter para Markdown", command=self.start_conversion, style="Accent.TButton")
        self.convert_button.pack(anchor="e", pady=(18, 0))
        self.root.after(100, self.poll_events)

        if initial_pdf:
            self.root.after(250, self.start_conversion)

    def choose_file(self):
        filename = filedialog.askopenfilename(title="Escolher PDF", filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")])
        if filename:
            self.file_var.set(filename)

    def choose_tessdata(self):
        folder = filedialog.askdirectory(title="Escolher a pasta tessdata")
        if folder:
            self.tessdata_var.set(folder)

    def start_conversion(self):
        if self.busy:
            return
        selected = self.file_var.get().strip()
        if not selected:
            selected = filedialog.askopenfilename(title="Escolher PDF", filetypes=[("Arquivos PDF", "*.pdf")])
            if not selected:
                return
            self.file_var.set(selected)
        lang = self.language_var.get().strip() if self.ocr_var.get() else None
        if self.ocr_var.get() and not lang:
            messagebox.showerror(APP_NAME, "Informe ao menos um idioma OCR, por exemplo por+eng.")
            return
        self.busy = True
        self.convert_button.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        self.progress.stop()
        self.progress.configure(mode="determinate", value=0)
        self.status_var.set("Iniciando a conversão…")

        tessdata = self.tessdata_var.get().strip() if self.ocr_var.get() else None

        def worker():
            try:
                destination = convert_pdf(Path(selected), lang, tessdata, self.events.put)
                self.events.put(("done", str(destination)))
            except Exception as exc:
                self.events.put(("error", str(exc), traceback.format_exc()))

        threading.Thread(target=worker, daemon=True).start()

    def poll_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "status":
                    self.status_var.set(event[1])
                elif event[0] == "progress":
                    self.progress.configure(mode="determinate", value=event[1])
                    if event[1] <= 90:
                        self.status_var.set(f"Processando páginas… {event[1]}%")
                elif event[0] in ("done", "error"):
                    self.progress.stop()
                    self.progress.configure(mode="determinate", value=100 if event[0] == "done" else 0)
                    self.busy = False
                    self.convert_button.configure(state="normal")
                    self.browse_button.configure(state="normal")
                    if event[0] == "done":
                        self.status_var.set("Conversão concluída.")
                        messagebox.showinfo(APP_NAME, f"Arquivo criado:\n{event[1]}")
                    else:
                        self.status_var.set("A conversão não foi concluída.")
                        messagebox.showerror(APP_NAME, event[1])
        except queue.Empty:
            pass
        self.root.after(100, self.poll_events)


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("pdf", nargs="?")
    args, _ = parser.parse_known_args(sys.argv[1:])
    if args.pdf and not Path(args.pdf).exists():
        messagebox.showerror(APP_NAME, f"O arquivo não foi encontrado:\n{args.pdf}")
        return 2
    root = tk.Tk()
    try:
        ttk.Style(root).theme_use("vista")
    except tk.TclError:
        pass
    ConverterApp(root, args.pdf)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
