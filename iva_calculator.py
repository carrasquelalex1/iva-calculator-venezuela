import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import csv
from datetime import datetime
from ttkthemes import ThemedTk  # Import ThemedTk

class AdvancedIVACalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de IVA Venezuela")

        # Variables de estado
        self.calculation_mode = tk.StringVar(value="saldo") # "saldo", "total", "sumar"
        self.sales = tk.StringVar()
        self.purchases = tk.StringVar()
        self.total_with_iva = tk.StringVar()
        self.original_price = tk.StringVar()
        self.iva_rate = tk.DoubleVar(value=16.0)
        self.credit_fiscal = tk.DoubleVar()
        self.debit_fiscal = tk.DoubleVar()
        self.balance = tk.DoubleVar()
        self.iva_amount_from_total = tk.DoubleVar()
        self.final_price_add_iva = tk.DoubleVar()
        self.iva_added_amount = tk.DoubleVar()
        self.transactions = []
        self.selected_transaction_index = None

        # Estilo ttk
        self.style = ttk.Style(root)
        self.style.configure('TButton', font=('Arial', 10), padding=8)
        self.style.configure('Calculate.TButton', background='#007bff', foreground='white', relief='flat')
        self.style.map('Calculate.TButton', background=[('active', '#0056b3')])
        self.style.configure('Export.TButton', background='#28a745', foreground='white', relief='flat')
        self.style.map('Export.TButton', background=[('active', '#1e7e34')])
        self.style.configure('Clear.TButton', background='#dc3545', foreground='white', relief='flat')
        self.style.map('Clear.TButton', background=[('active', '#bd2130')])
        self.style.configure('Edit.TButton', background='#ffc107', foreground='black', relief='flat')
        self.style.map('Edit.TButton', background=[('active', '#ffb300')])
        self.style.configure('Delete.TButton', background='#6c757d', foreground='white', relief='flat')
        self.style.map('Delete.TButton', background=[('active', '#5a6268')])

        self.create_widgets()

    def create_widgets(self):
        # Título
        title_label = ttk.Label(self.root, text="Calculadora de IVA Venezuela", font=("Arial", 18, "bold"))
        title_label.pack(pady=20)

        # Frame para modos de cálculo
        mode_frame = ttk.Frame(self.root)
        mode_frame.pack(pady=10)

        ttk.Radiobutton(mode_frame, text="Calcular Saldo de IVA (Ventas y Compras)", variable=self.calculation_mode, value="saldo", command=self.update_input_visibility).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Calcular IVA de un Total (IVA Incluido)", variable=self.calculation_mode, value="total", command=self.update_input_visibility).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Sumar IVA a un Precio (Añadir IVA)", variable=self.calculation_mode, value="sumar", command=self.update_input_visibility).pack(side=tk.LEFT, padx=10)

        # Frame para entradas
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill=tk.X)

        # Entradas para modo "Saldo de IVA"
        self.sales_label = ttk.Label(input_frame, text="Ventas Gravadas (Bs.S):", width=20, anchor='w')
        self.sales_entry = ttk.Entry(input_frame, textvariable=self.sales)
        self.purchases_label = ttk.Label(input_frame, text="Compras Gravadas (Bs.S):", width=20, anchor='w')
        self.purchases_entry = ttk.Entry(input_frame, textvariable=self.purchases)

        self.sales_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.sales_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.purchases_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.purchases_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.sales_entry.focus()

        # Entrada para modo "IVA de un Total"
        self.total_iva_label = ttk.Label(input_frame, text="Total con IVA (Bs.S):", width=20, anchor='w')
        self.total_iva_entry = ttk.Entry(input_frame, textvariable=self.total_with_iva)

        # Entrada para modo "Sumar IVA a un Precio"
        self.original_price_label = ttk.Label(input_frame, text="Precio Original (Bs.S):", width=20, anchor='w')
        self.original_price_entry = ttk.Entry(input_frame, textvariable=self.original_price)

        ttk.Label(input_frame, text="Tasa de IVA (%):", width=20, anchor='w').grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        iva_rate_entry = ttk.Entry(input_frame, textvariable=self.iva_rate, width=10)
        iva_rate_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(input_frame, text="%", anchor='w').grid(row=4, column=2, padx=0, pady=5, sticky="w")

        input_frame.columnconfigure(1, weight=1)

        # Frame para botón de cálculo
        calculate_frame = ttk.Frame(self.root)
        calculate_frame.pack(pady=10)
        calculate_button = ttk.Button(calculate_frame, text="Calcular", command=self.perform_calculation, style='Calculate.TButton')
        calculate_button.pack(pady=5)

        # Resultados
        results_frame = ttk.Frame(self.root)
        results_frame.pack(pady=10, padx=20, fill=tk.X)

        # Resultados para modo "Saldo de IVA"
        self.debit_label = ttk.Label(results_frame, text="Débito Fiscal (IVA Cobrado):", width=30, anchor='w')
        self.debit_result_label = ttk.Label(results_frame, textvariable=self.debit_fiscal)
        self.credit_label = ttk.Label(results_frame, text="Crédito Fiscal (IVA Pagado):", width=30, anchor='w')
        self.credit_result_label = ttk.Label(results_frame, textvariable=self.credit_fiscal)
        self.balance_label = ttk.Label(results_frame, text="Total IVA a Pagar/Devolver:", width=30, anchor='w', font=("Arial", 10, "bold"))
        self.balance_result_label = ttk.Label(results_frame, textvariable=self.balance, font=("Arial", 10, "bold"))

        self.debit_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.debit_result_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.credit_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.credit_result_label.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.balance_label.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.balance_result_label.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Resultados para modo "IVA de un Total"
        self.iva_from_total_label = ttk.Label(results_frame, text="IVA dentro del Total:", width=30, anchor='w', font=("Arial", 10, "bold"))
        self.iva_from_total_result_label = ttk.Label(results_frame, textvariable=self.iva_amount_from_total, font=("Arial", 10, "bold"))

        # Resultados para modo "Sumar IVA a un Precio"
        self.final_price_label = ttk.Label(results_frame, text="Precio Final (IVA Incluido):", width=30, anchor='w', font=("Arial", 10, "bold"))
        self.final_price_result_label = ttk.Label(results_frame, textvariable=self.final_price_add_iva, font=("Arial", 10, "bold"))
        self.iva_added_label = ttk.Label(results_frame, text="IVA Añadido:", width=30, anchor='w')
        self.iva_added_result_label = ttk.Label(results_frame, textvariable=self.iva_added_amount)

        results_frame.columnconfigure(1, weight=1)

        # Historial de transacciones
        history_frame = ttk.Frame(self.root)
        history_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        ttk.Label(history_frame, text="Historial de Transacciones", font=("Arial", 14, "bold")).pack(pady=(0,5), anchor='w')

        self.tree = ttk.Treeview(history_frame, columns=("Fecha", "Modo", "Ventas", "Compras", "Total con IVA", "Precio Original", "Tasa IVA (%)", "Débito", "Crédito", "IVA del Total", "IVA Añadido", "Saldo", "Precio Final"), show="headings")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Modo", text="Modo")
        self.tree.heading("Ventas", text="Ventas (Bs.S)")
        self.tree.heading("Compras", text="Compras (Bs.S)")
        self.tree.heading("Total con IVA", text="Total con IVA (Bs.S)")
        self.tree.heading("Precio Original", text="Precio Original (Bs.S)")
        self.tree.heading("Tasa IVA (%)", text="Tasa IVA (%)")
        self.tree.heading("Débito", text="Débito Fiscal (Bs.S)")
        self.tree.heading("Crédito", text="Crédito Fiscal (Bs.S)")
        self.tree.heading("IVA del Total", text="IVA del Total (Bs.S)")
        self.tree.heading("IVA Añadido", text="IVA Añadido (Bs.S)")
        self.tree.heading("Saldo", text="Total IVA (Bs.S)")
        self.tree.heading("Precio Final", text="Precio Final (Bs.S)")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.select_transaction)

        history_button_frame = ttk.Frame(history_frame)
        history_button_frame.pack(pady=5, fill=tk.X)

        self.edit_button = ttk.Button(history_button_frame, text="Editar", command=self.edit_transaction, style='Edit.TButton', state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.delete_button = ttk.Button(history_button_frame, text="Eliminar", command=self.delete_transaction, style='Delete.TButton', state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        export_button = ttk.Button(history_button_frame, text="Exportar a CSV", command=self.export_to_csv, style='Export.TButton')
        export_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        clear_button = ttk.Button(history_button_frame, text="Limpiar Historial", command=self.clear_history, style='Clear.TButton')
        clear_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        history_button_frame.columnconfigure(0, weight=1)
        history_button_frame.columnconfigure(1, weight=1)
        history_button_frame.columnconfigure(2, weight=1)
        history_button_frame.columnconfigure(3, weight=1)

        self.history_message_label = ttk.Label(history_frame, text="* Editar para 'IVA del Total' permite cambiar Tasa IVA y Total con IVA. Editar para 'Saldo IVA' permite cambiar Ventas, Compras y Tasa IVA. Editar para 'Sumar IVA a un Precio' permite cambiar Precio Original y Tasa IVA.", font=("Arial", 8), foreground="gray")
        self.history_message_label.pack(side=tk.BOTTOM, anchor='w', padx=5)

        self.update_input_visibility()

    def update_input_visibility(self):
        if self.calculation_mode.get() == "saldo":
            # Mostrar campos para "Saldo de IVA"
            self.sales_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.sales_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.purchases_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
            self.purchases_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.total_iva_label.grid_forget()
            self.total_iva_entry.grid_forget()
            self.original_price_label.grid_forget()
            self.original_price_entry.grid_forget()

            # Mostrar resultados para "Saldo de IVA"
            self.debit_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.debit_result_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.credit_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
            self.credit_result_label.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.balance_label.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
            self.balance_result_label.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
            self.iva_from_total_label.grid_forget()
            self.iva_from_total_result_label.grid_forget()
            self.final_price_label.grid_forget()
            self.final_price_result_label.grid_forget()
            self.iva_added_label.grid_forget()
            self.iva_added_result_label.grid_forget()
            self.enable_history_buttons()

        elif self.calculation_mode.get() == "total":
            # Mostrar campo para "Total con IVA"
            self.total_iva_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.total_iva_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.sales_label.grid_forget()
            self.sales_entry.grid_forget()
            self.purchases_label.grid_forget()
            self.purchases_entry.grid_forget()
            self.original_price_label.grid_forget()
            self.original_price_entry.grid_forget()

            # Mostrar resultado para "IVA de un Total"
            self.iva_from_total_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.iva_from_total_result_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.debit_label.grid_forget()
            self.debit_result_label.grid_forget()
            self.credit_label.grid_forget()
            self.credit_result_label.grid_forget()
            self.balance_label.grid_forget()
            self.balance_result_label.grid_forget()
            self.final_price_label.grid_forget()
            self.final_price_result_label.grid_forget()
            self.iva_added_label.grid_forget()
            self.iva_added_result_label.grid_forget()
            self.enable_history_buttons()

        elif self.calculation_mode.get() == "sumar":
            # Mostrar campos para "Sumar IVA a un Precio"
            self.original_price_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.original_price_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.sales_label.grid_forget()
            self.sales_entry.grid_forget()
            self.purchases_label.grid_forget()
            self.purchases_entry.grid_forget()
            self.total_iva_label.grid_forget()
            self.total_iva_entry.grid_forget()

            # Mostrar resultados para "Sumar IVA a un Precio"
            self.final_price_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.final_price_result_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.iva_added_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
            self.iva_added_result_label.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.debit_label.grid_forget()
            self.debit_result_label.grid_forget()
            self.credit_label.grid_forget()
            self.credit_result_label.grid_forget()
            self.balance_label.grid_forget()
            self.balance_result_label.grid_forget()
            self.iva_from_total_label.grid_forget()
            self.iva_from_total_result_label.grid_forget()
            self.enable_history_buttons()


    def perform_calculation(self):
        if self.calculation_mode.get() == "saldo":
            self.calculate_balance()
        elif self.calculation_mode.get() == "total":
            self.calculate_iva_from_total()
        elif self.calculation_mode.get() == "sumar":
            self.calculate_add_iva()


    def calculate_balance(self):
        try:
            sales_amount = float(self.sales.get())
            purchases_amount = float(self.purchases.get())
            rate = float(self.iva_rate.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos para Ventas, Compras y Tasa de IVA.")
            return

        debit = (sales_amount * rate) / 100
        credit = (purchases_amount * rate) / 100
        balance_result = debit - credit

        self.debit_fiscal.set(f"{debit:,.2f}")
        self.credit_fiscal.set(f"{credit:,.2f}")
        self.balance.set(f"{balance_result:,.2f}")
        self.iva_amount_from_total.set("")
        self.final_price_add_iva.set("")
        self.iva_added_amount.set("")


        new_transaction = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "Saldo IVA",
            "sales": round(sales_amount, 2),
            "purchases": round(purchases_amount, 2),
            "total_with_iva": 0,
            "precio_original": 0,
            "iva_rate": rate,
            "debit": round(debit, 2),
            "credit": round(credit, 2),
            "iva_from_total": 0,
            "iva_added": 0,
            "balance": round(balance_result, 2),
            "precio_final": 0
        }
        self.transactions.insert(0, new_transaction)
        self.update_transaction_table()

        self.sales.set("")
        self.purchases.set("")
        self.iva_rate.set(16.0)


    def calculate_iva_from_total(self):
        try:
            total_amount = float(self.total_with_iva.get())
            rate = float(self.iva_rate.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos para Total con IVA y Tasa de IVA.")
            return

        iva_factor = 1 + (rate / 100)
        iva_amount = total_amount - (total_amount / iva_factor)

        self.iva_amount_from_total.set(f"{iva_amount:,.2f}")
        self.debit_fiscal.set("")
        self.credit_fiscal.set("")
        self.balance.set("")
        self.final_price_add_iva.set("")
        self.iva_added_amount.set("")


        new_transaction = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "IVA del Total",
            "sales": 0,
            "purchases": 0,
            "total_with_iva": round(total_amount, 2),
            "precio_original": 0,
            "iva_rate": rate,
            "debit": 0,
            "credit": 0,
            "iva_from_total": round(iva_amount, 2),
            "iva_added": 0,
            "balance": 0,
            "precio_final": 0
        }
        self.transactions.insert(0, new_transaction)
        self.update_transaction_table()


        self.total_with_iva.set("")
        self.iva_rate.set(16.0)


    def calculate_add_iva(self):
        try:
            original_price_amount = float(self.original_price.get())
            rate = float(self.iva_rate.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos para Precio Original y Tasa de IVA.")
            return

        iva_amount = (original_price_amount * rate) / 100
        final_price = original_price_amount + iva_amount

        self.final_price_add_iva.set(f"{final_price:,.2f}")
        self.iva_added_amount.set(f"{iva_amount:,.2f}")
        self.debit_fiscal.set("")
        self.credit_fiscal.set("")
        self.balance.set("")
        self.iva_amount_from_total.set("")

        new_transaction = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "Sumar IVA",
            "sales": 0,
            "purchases": 0,
            "total_with_iva": 0,
            "precio_original": round(original_price_amount, 2),
            "iva_rate": rate,
            "debit": 0,
            "credit": 0,
            "iva_from_total": 0,
            "iva_added": round(iva_amount, 2),
            "balance": 0,
            "precio_final": round(final_price, 2)
        }
        self.transactions.insert(0, new_transaction)
        self.update_transaction_table()

        self.original_price.set("")
        self.iva_rate.set(16.0)


    def update_transaction_table(self):
        self.tree.delete(*self.tree.get_children())
        for transaction in self.transactions:
            if transaction["mode"] == "Saldo IVA":
                self.tree.insert("", "end", values=(
                    transaction["date"],
                    transaction["mode"],
                    f"{transaction['sales']:,.2f}",
                    f"{transaction['purchases']:,.2f}",
                    "",
                    "",
                    transaction["iva_rate"],
                    f"{transaction['debit']:,.2f}",
                    f"{transaction['credit']:,.2f}",
                    "",
                    "",
                    f"{transaction['balance']:,.2f}",
                    ""
                ))
            elif transaction["mode"] == "IVA del Total":
                self.tree.insert("", "end", values=(
                    transaction["date"],
                    transaction["mode"],
                    "",
                    "",
                    f"{transaction['total_with_iva']:,.2f}",
                    "",
                    transaction["iva_rate"],
                    "",
                    "",
                    f"{transaction['iva_from_total']:,.2f}",
                    "",
                    "",
                    ""
                ))
            elif transaction["mode"] == "Sumar IVA":
                self.tree.insert("", "end", values=(
                    transaction["date"],
                    transaction["mode"],
                    "",
                    "",
                    "",
                    f"{transaction['precio_original']:,.2f}",
                    transaction["iva_rate"],
                    "",
                    "",
                    "",
                    f"{transaction['iva_added']:,.2f}",
                    "",
                    f"{transaction['precio_final']:,.2f}"
                ))


    def export_to_csv(self):
        if not self.transactions:
            messagebox.showinfo("Información", "No hay transacciones para exportar.")
            return

        file_path = "historial_iva.csv"
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Fecha", "Modo", "Ventas", "Compras", "Total con IVA", "Precio Original", "Tasa IVA (%)", "Débito Fiscal", "Crédito Fiscal", "IVA del Total", "IVA Añadido", "Saldo", "Precio Final"])
            for transaction in self.transactions:
                writer.writerow([
                    transaction["date"],
                    transaction["mode"],
                    transaction["sales"],
                    transaction["purchases"],
                    transaction["total_with_iva"],
                    transaction["precio_original"],
                    transaction["iva_rate"],
                    transaction["debit"],
                    transaction["credit"],
                    transaction["iva_from_total"],
                    transaction["iva_added"],
                    transaction["balance"],
                    transaction["precio_final"]
                ])
        messagebox.showinfo("Éxito", f"Historial exportado a {file_path}")

    def clear_history(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres limpiar el historial de transacciones?"):
            self.transactions = []
            self.update_transaction_table()
            self.disable_history_buttons()
            messagebox.showinfo("Información", "Historial de transacciones limpiado.")

    def select_transaction(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.selected_transaction_index = self.tree.index(row_id)
            self.enable_history_buttons()
        else:
            self.disable_history_buttons()

    def enable_history_buttons(self):
        self.edit_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)

    def disable_history_buttons(self):
        self.edit_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.tree.selection_remove(self.tree.selection())

    def delete_transaction(self):
        if self.selected_transaction_index is not None:
            if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar este registro?"):
                del self.transactions[self.selected_transaction_index]
                self.update_transaction_table()
                self.disable_history_buttons()
                self.selected_transaction_index = None
                messagebox.showinfo("Información", "Registro eliminado del historial.")
        else:
            messagebox.showinfo("Advertencia", "Por favor, selecciona un registro para eliminar.")

    def edit_transaction(self):
        if self.selected_transaction_index is not None:
            selected_transaction = self.transactions[self.selected_transaction_index]
            if selected_transaction["mode"] == "Saldo IVA":
                EditTransactionDialog(self.root, selected_transaction, self.selected_transaction_index, self.update_transaction)
            elif selected_transaction["mode"] == "IVA del Total":
                EditTotalIvaTransactionDialog(self.root, selected_transaction, self.selected_transaction_index, self.update_transaction)
            elif selected_transaction["mode"] == "Sumar IVA":
                EditAddIvaTransactionDialog(self.root, selected_transaction, self.selected_transaction_index, self.update_transaction)
        else:
            messagebox.showinfo("Advertencia", "Por favor, selecciona un registro para editar.")

    def update_transaction(self, index, updated_transaction_data):
        self.transactions[index] = updated_transaction_data
        self.update_transaction_table()
        messagebox.showinfo("Información", "Registro del historial actualizado.")


class EditTransactionDialog(tk.Toplevel):
    def __init__(self, parent, transaction_data, transaction_index, update_callback):
        super().__init__(parent)
        self.title("Editar Registro - Saldo IVA")
        self.transient(parent)
        self.grab_set()

        self.transaction_index = transaction_index
        self.update_callback = update_callback

        self.sales_var = tk.StringVar(value=transaction_data['sales'])
        self.purchases_var = tk.StringVar(value=transaction_data['purchases'])
        self.iva_rate_var = tk.DoubleVar(value=transaction_data['iva_rate'])

        ttk.Label(self, text="Ventas Gravadas (Bs.S):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.sales_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Compras Gravadas (Bs.S):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.purchases_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Tasa de IVA (%):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.iva_rate_var).grid(row=2, column=1, padx=5, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        save_button = ttk.Button(button_frame, text="Guardar", command=self.save_changes, style='Calculate.TButton')
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.cancel_edit, style='Clear.TButton')
        cancel_button.pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.cancel_edit)
        self.wait_window(self)


    def save_changes(self):
        try:
            updated_sales = float(self.sales_var.get())
            updated_purchases = float(self.purchases_var.get())
            updated_iva_rate = float(self.iva_rate_var.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores válidos.")
            return

        debit = (updated_sales * updated_iva_rate) / 100
        credit = (updated_purchases * updated_iva_rate) / 100
        balance_result = debit - credit

        updated_transaction_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "Saldo IVA",
            "sales": round(updated_sales, 2),
            "purchases": round(updated_purchases, 2),
            "total_with_iva": 0,
            "precio_original": 0,
            "iva_rate": updated_iva_rate,
            "debit": round(debit, 2),
            "credit": round(credit, 2),
            "iva_from_total": 0,
            "iva_added": 0,
            "balance": round(balance_result, 2),
            "precio_final": 0
        }
        self.update_callback(self.transaction_index, updated_transaction_data)
        self.destroy()

    def cancel_edit(self):
        self.destroy()


class EditTotalIvaTransactionDialog(tk.Toplevel):
    def __init__(self, parent, transaction_data, transaction_index, update_callback):
        super().__init__(parent)
        self.title("Editar Registro - IVA del Total")
        self.transient(parent)
        self.grab_set()

        self.transaction_index = transaction_index
        self.update_callback = update_callback

        self.total_iva_var = tk.StringVar(value=transaction_data['total_with_iva'])
        self.iva_rate_var = tk.DoubleVar(value=transaction_data['iva_rate'])

        ttk.Label(self, text="Total con IVA (Bs.S):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.total_iva_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Tasa de IVA (%):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.iva_rate_var).grid(row=1, column=1, padx=5, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        save_button = ttk.Button(button_frame, text="Guardar", command=self.save_changes, style='Calculate.TButton')
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.cancel_edit, style='Clear.TButton')
        cancel_button.pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.cancel_edit)
        self.wait_window(self)


    def save_changes(self):
        try:
            updated_total_iva = float(self.total_iva_var.get())
            updated_iva_rate = float(self.iva_rate_var.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores válidos.")
            return

        iva_factor = 1 + (updated_iva_rate) / 100
        updated_iva_amount = updated_total_iva - (updated_total_iva / iva_factor)

        updated_transaction_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "IVA del Total",
            "sales": 0,
            "purchases": 0,
            "total_with_iva": round(updated_total_iva, 2),
            "precio_original": 0,
            "iva_rate": updated_iva_rate,
            "debit": 0,
            "credit": 0,
            "iva_from_total": round(updated_iva_amount, 2),
            "iva_added": 0,
            "balance": 0,
            "precio_final": 0
        }
        self.update_callback(self.transaction_index, updated_transaction_data)
        self.destroy()

    def cancel_edit(self):
        self.destroy()


class EditAddIvaTransactionDialog(tk.Toplevel):
    def __init__(self, parent, transaction_data, transaction_index, update_callback):
        super().__init__(parent)
        self.title("Editar Registro - Sumar IVA")
        self.transient(parent)
        self.grab_set()

        self.transaction_index = transaction_index
        self.update_callback = update_callback

        self.original_price_var = tk.StringVar(value=transaction_data['precio_original'])
        self.iva_rate_var = tk.DoubleVar(value=transaction_data['iva_rate'])

        ttk.Label(self, text="Precio Original (Bs.S):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.original_price_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Tasa de IVA (%):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.iva_rate_var).grid(row=1, column=1, padx=5, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        save_button = ttk.Button(button_frame, text="Guardar", command=self.save_changes, style='Calculate.TButton')
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.cancel_edit, style='Clear.TButton')
        cancel_button.pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.cancel_edit)
        self.wait_window(self)


    def save_changes(self):
        try:
            updated_original_price = float(self.original_price_var.get())
            updated_iva_rate = float(self.iva_rate_var.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos.")
            return

        updated_iva_amount = (updated_original_price * updated_iva_rate) / 100
        updated_final_price = updated_original_price + updated_iva_amount

        updated_transaction_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "Sumar IVA",
            "sales": 0,
            "purchases": 0,
            "total_with_iva": 0,
            "precio_original": round(updated_original_price, 2),
            "iva_rate": updated_iva_rate,
            "debit": 0,
            "credit": 0,
            "iva_from_total": 0,
            "iva_added": round(updated_iva_amount, 2),
            "balance": 0,
            "precio_final": round(updated_final_price, 2)
        }
        self.update_callback(self.transaction_index, updated_transaction_data)
        self.destroy()

    def cancel_edit(self):
        self.destroy()


# Ejecutar la aplicación
if __name__ == "__main__":
    root = ThemedTk(theme="clam")
    try:
        root.attributes('-zoomed', True)
    except tk.TclError:
        root.state('zoomed')
    app = AdvancedIVACalculator(root)
    root.mainloop()
