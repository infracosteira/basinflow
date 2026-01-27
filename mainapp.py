#myapp.py
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

FILE_SCHEMAS = {
    "reservoir.dat": {
        "names": ['subasin_id', 'water_storage_capacity', 'dam_height', 'spillway_discharge'],
        "decimal": ","
    },
    "routing.dat": {
        "names": ['subasin_id', 'upstream', 'downstream'],
        "decimal": "."
    },
    "runoff.dat": {
        "names": ['subasin_id', 'runoff_volume', 'runoff_peak_discharge'],
        "decimal": "."
    },
    "sedyield.dat": {
        "names": ['subasin_id', 'sed_enter_volume'],
        "decimal": "."
    }
}

dataframes = {}

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(levelname)s: %(message)s'
logging.basicConfig(filename='myapp.log', level=logging.INFO,format=FORMAT)
logger.info('Started')

def clean_dataframe_columns(df, exclude_cols=None):
    if exclude_cols is None: exclude_cols = []
    for col in df.columns:
        if col not in exclude_cols:
            df[col] = (
                df[col].astype(str)
                .str.replace('"', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
    return df

def selecionar_arquivo(entry_widget, chave):
    file_path = filedialog.askopenfilename(
        title=f"Selecionar arquivo {chave}",
        filetypes=[("Arquivos DAT", "*.dat"), ("Todos os arquivos", "*.*")]
    )

    if not file_path:
        return

    entry_widget.config(state=tk.NORMAL)
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, file_path)
    entry_widget.config(state=tk.DISABLED)

    try:
        config = FILE_SCHEMAS[chave]

        df = pd.read_table(
            file_path,
            encoding='latin1',
            skiprows=2,
            names=config["names"],
            decimal=config.get("decimal", "."),
            sep=r'\s+',
            engine='python'
        )

        df = clean_dataframe_columns(df, exclude_cols=['subasin_id'])

        # 🔥 salva com identidade correta
        dataframes[chave] = df

        print(f"\nArquivo '{chave}' carregado com sucesso")
        print(df.head())
        
        txt_saida['state'] = tk.NORMAL
        txt_saida.insert(tk.END, f"Arquivo '{chave}' carregado com sucesso\n")
        txt_saida.see(tk.END)
        txt_saida['state'] = tk.DISABLED

        #txt_saida.insert(tk.END, df.head().to_string() + "\n")

        txt_saida.see(tk.END)

    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Erro ao ler o arquivo {chave}:\n{e}"
        )
        txt_saida.insert(tk.END, f"Erro ao ler o arquivo {chave}:\n{e}\n")
        txt_saida.see(tk.END)


def toggle_sedimentos():
    
    # Define o estado com base no valor do checkbox
    novo_estado = tk.NORMAL if ativar.get() else tk.DISABLED
    #                NORMAL = HABILITADO DISABLED = DESABILITADO
    # Lista de componentes que devem ser habilitados/desabilitados
    componentes = [ent_sed, btn_sed, rb_file, rb_manual, ent_param_file, btn_param_file, ent_density, ent_efficiency]
    
    for comp in componentes:
        comp.config(state=novo_estado)

# --- Interface Principal ---
root = tk.Tk()
root.title("Simulador Hidrológico")
root.geometry("650x800")

# 1. ENTRADA DE DADOS
frame_entrada = tk.LabelFrame(root, text="Entrada de dados", padx=10, pady=10)
# pad adiciona espaço interno

frame_entrada.pack(fill="x", padx=20, pady=10)
#o pack com fill="x" faz o frame ocupar toda a largura disponível, então esse retagunlo em especifico
#vai ser o retangulo que engloba toda a seção de entrada de dados
labels = ["routing.dat", "runoff.dat", "reservoir.dat"]
entradas_principais = {}

for label in labels:
    row = tk.Frame(frame_entrada)
    row.pack(fill="x", pady=2)

    tk.Label(row, text=f"Carregar arquivo {label}:", width=25, anchor="w").pack(side="left")

    ent = tk.Entry(row, state=tk.DISABLED)
    ent.pack(side="left", expand=True, fill="x", padx=5)

    entradas_principais[label] = ent

    tk.Button(
        row,
        text="...",
        command=lambda e=ent, l=label: selecionar_arquivo(e, l)
    ).pack(side="right")


# 2. SIMULAR DINÂMICA DE SEDIMENTOS
ativar = tk.BooleanVar(value=False) # Começa DESMARCADA
frame_sedimentos = tk.LabelFrame(root, padx=15, pady=10)
frame_sedimentos.pack(fill="x", padx=20, pady=10)

check_btn = tk.Checkbutton(frame_sedimentos, text="Simular dinâmica de sedimentos", 
                           variable=ativar, command=toggle_sedimentos, font=('Arial', 10, 'bold'))

frame_sedimentos.configure(labelwidget=check_btn)

# Linha do arquivo sedyield.dat
row_sed = tk.Frame(frame_sedimentos)
row_sed.pack(fill="x", pady=5)
tk.Label(row_sed, text="Carregar arquivo sedyield.dat:", width=25, anchor="w").pack(side="left")
ent_sed = tk.Entry(row_sed, state=tk.DISABLED)
ent_sed.pack(side="left", expand=True, fill="x", padx=5)
btn_sed = tk.Button(row_sed, text="...", state=tk.DISABLED, command=lambda: selecionar_arquivo(ent_sed, "sedyield.dat"))
btn_sed.pack(side="right")

# Sub-seção Parâmetros Sedimentológicos

subframe_params = tk.LabelFrame(frame_sedimentos, text="Parâmetros sedimentológicos", padx=10, pady=10)
subframe_params.pack(fill="x", pady=5)

radio_var = tk.IntVar(value=1)

# Opção 1: Carregar do arquivo
row_p1 = tk.Frame(subframe_params)
row_p1.pack(fill="x")
rb_file = tk.Radiobutton(row_p1, text="Carregar do arquivo:", variable=radio_var, value=1, state=tk.DISABLED)
rb_file.pack(side="left")
ent_param_file = tk.Entry(row_p1, state=tk.DISABLED)
ent_param_file.pack(side="left", expand=True, fill="x", padx=5)
btn_param_file = tk.Button(row_p1, text="...", state=tk.DISABLED, command=lambda: selecionar_arquivo(ent_param_file))
btn_param_file.pack(side="right")

# Opção 2: Valores manuais
rb_manual = tk.Radiobutton(subframe_params, text="Utilizar valores abaixo:", variable=radio_var, value=2, state=tk.DISABLED)
rb_manual.pack(anchor="w")

# Campos de densidade e eficiência
row_manual = tk.Frame(subframe_params)
row_manual.pack(fill="x", padx=20)
tk.Label(row_manual, text="Sediment density - dry clay (g/cm³):").grid(row=0, column=0, sticky="w")
ent_density = tk.Entry(row_manual, width=10, state=tk.DISABLED)
ent_density.insert(0, "1,5")
ent_density.grid(row=0, column=1, padx=5, pady=2)

tk.Label(row_manual, text="Sediment retention efficiency (%):").grid(row=1, column=0, sticky="w")
ent_efficiency = tk.Entry(row_manual, width=10, state=tk.DISABLED)
ent_efficiency.insert(0, "50%")
ent_efficiency.grid(row=1, column=1, padx=5, pady=2)

# 3. BOTÃO CALCULAR
btn_calcular = tk.Button(root, command=None ,  text="Calcular", bg="#d9d9d9", font=('Arial', 12, 'bold'), height=2)
btn_calcular.pack(pady=15, padx=20, fill="x")

# 4. ÁREA DE SAÍDA (LOG)
frame_saida = tk.LabelFrame(root, text="Saída", padx=10, pady=10)
frame_saida.pack(fill="both", expand=True, padx=20, pady=10)
txt_saida = tk.Text(frame_saida, height=6, bg="#ffffff", state=tk.DISABLED)
txt_saida.pack(fill="both", expand=True)


root.mainloop()


logger.info('Finished')