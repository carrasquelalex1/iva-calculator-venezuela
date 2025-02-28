import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import csv
from datetime import datetime
from ttkthemes import ThemedTk  # Import ThemedTk

class AdvancedIVACalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de IVA Avanzada (Venezuela)")
        # self.root.geometry("800x600") # Remove fixed geometry, let it expand

        # Variables de estado
        self.sales = tk.StringVar()
        self.purchases = tk.StringVar()
        self.iva_rate = tk.DoubleVar(value=16.0)
        self.credit_fiscal = tk.DoubleVar()
        self.debit_fiscal = tk.DoubleVar()
        self.balance = tk.DoubleVar()
        self.transactions = []
        self.selected_transaction_index = None # To keep track of selected row index

        # Estilo ttk con colores personalizados
        self.style = ttk.Style(root)

        # --- Estilos de Botones ---
        self.style.configure('TButton', font=('Arial', 10), padding=6)
        self.style.configure('Calculate.TButton', background='#4CAF50', foreground='white', relief='raised')
        self.style.map('Calculate.TButton', background=[('active', '#43A047'), ('disabled', '#C8E6C9')])
        self.style.configure('Export.TButton', background='#2196F3', foreground='white', relief='raised')
        self.style.map('Export.TButton', background=[('active', '#1976D2'), ('disabled', '#BBDEFB')])
        self.style.configure('Clear.TButton', background='#FF9800', foreground='white', relief='raised')
        self.style.map('Clear.TButton', background=[('active', '#F57C00'), ('disabled', '#FFCC80')])
        self.style.configure('Edit.TButton', background='#FFC107', foreground='black', relief='raised') # Yellow for Edit
        self.style.map('Edit.TButton', background=[('active', '#FFB300'), ('disabled', '#FFECB3')])
        self.style.configure('Delete.TButton', background='#F44336', foreground='white', relief='raised') # Red for Delete
        self.style.map('Delete.TButton', background=[('active', '#D32F2F'), ('disabled', '#FFCDD2')])


        # Diseño de la interfaz
        self.create_widgets()

    def create_widgets(self):
        # Título
        title_label = ttk.Label(self.root, text="Calculadora de IVA Avanzada (Venezuela)", font=("Arial", 16))
        title_label.pack(pady=20)

        # Entradas
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10)

        ttk.Label(input_frame, text="Ventas Gravadas:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.sales).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Compras Gravadas:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.purchases).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Tasa de IVA (%):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.iva_rate).grid(row=2, column=1, padx=5, pady=5)

        # Frame para botones de cálculo/exportación/limpiar
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        calculate_button = ttk.Button(button_frame, text="Calcular Saldo de IVA", command=self.calculate_balance, style='Calculate.TButton')
        calculate_button.pack(side=tk.LEFT, padx=5)

        export_button = ttk.Button(button_frame, text="Exportar Historial a CSV", command=self.export_to_csv, style='Export.TButton')
        export_button.pack(side=tk.LEFT, padx=5)

        clear_button = ttk.Button(button_frame, text="Limpiar Historial", command=self.clear_history, style='Clear.TButton')
        clear_button.pack(side=tk.LEFT, padx=5)


        # Resultados
        results_frame = ttk.Frame(self.root)
        results_frame.pack(pady=10)

        ttk.Label(results_frame, text="Débito Fiscal (IVA Cobrado):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(results_frame, textvariable=self.debit_fiscal).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Crédito Fiscal (IVA Pagado):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(results_frame, textvariable=self.credit_fiscal).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(results_frame, text="Saldo a Pagar/Devolver:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(results_frame, textvariable=self.balance).grid(row=2, column=1, padx=5, pady=5)

        # Historial de transacciones
        history_frame = ttk.Frame(self.root)
        history_frame.pack(pady=10)

        ttk.Label(history_frame, text="Historial de Transacciones", font=("Arial", 14)).pack()

        self.tree = ttk.Treeview(history_frame, columns=("Fecha", "Ventas", "Compras", "Tasa IVA (%)", "Débito", "Crédito", "Saldo"), show="headings") # Added "Tasa IVA (%)"
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Ventas", text="Ventas")
        self.tree.heading("Compras", text="Compras")
        self.tree.heading("Tasa IVA (%)", text="Tasa IVA (%)") # Header for new column
        self.tree.heading("Débito", text="Débito Fiscal")
        self.tree.heading("Crédito", text="Crédito Fiscal")
        self.tree.heading("Saldo", text="Saldo")
        self.tree.pack()

        self.tree.bind("<ButtonRelease-1>", self.select_transaction) # Bind click event to select row

        # Frame for Edit/Delete buttons (below history table)
        history_button_frame = ttk.Frame(history_frame)
        history_button_frame.pack(pady=5)

        self.edit_button = ttk.Button(history_button_frame, text="Editar Registro", command=self.edit_transaction, style='Edit.TButton', state=tk.DISABLED) # Initially disabled
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(history_button_frame, text="Eliminar Registro", command=self.delete_transaction, style='Delete.TButton', state=tk.DISABLED) # Initially disabled
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # Label de agradecimiento al final
        footer_label = ttk.Label(self.root, text="Creado por Alexander Carrasquel. Agradecer no cuesta nada. https://www.linkedin.com/in/alexander-carrasquel-41a616108/", font=("Arial", 8))
        footer_label.pack(pady=5, side=tk.BOTTOM) # Pack al final y abajo


    def calculate_balance(self):
        try:
            sales_amount = float(self.sales.get())
            purchases_amount = float(self.purchases.get())
            rate = float(self.iva_rate.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores válidos.")
            return

        debit = (sales_amount * rate) / 100
        credit = (purchases_amount * rate) / 100
        balance_result = debit - credit

        self.debit_fiscal.set(round(debit, 2))
        self.credit_fiscal.set(round(credit, 2))
        self.balance.set(round(balance_result, 2))

        new_transaction = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sales": round(sales_amount, 2),
            "purchases": round(purchases_amount, 2),
            "iva_rate": rate, # Storing IVA rate here
            "debit": round(debit, 2),
            "credit": round(credit, 2),
            "balance": round(balance_result, 2),
        }
        self.transactions.insert(0, new_transaction)
        self.update_transaction_table()

        self.sales.set("")
        self.purchases.set("")
        self.iva_rate.set(16.0) # Reset IVA rate to default after calculation

    def update_transaction_table(self):
        self.tree.delete(*self.tree.get_children())
        for transaction in self.transactions:
            self.tree.insert("", "end", values=(
                transaction["date"],
                transaction["sales"],
                transaction["purchases"],
                transaction["iva_rate"], # Displaying IVA rate in the table
                transaction["debit"],
                transaction["credit"],
                transaction["balance"]
            ))

    def export_to_csv(self):
        if not self.transactions:
            messagebox.showinfo("Información", "No hay transacciones para exportar.")
            return

        file_path = "historial_iva.csv"
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Fecha", "Ventas", "Compras", "Tasa IVA (%)", "Débito Fiscal", "Crédito Fiscal", "Saldo"]) # Added "Tasa IVA (%)" to header
            for transaction in self.transactions:
                writer.writerow([
                    transaction["date"],
                    transaction["sales"],
                    transaction["purchases"],
                    transaction["iva_rate"], # Exporting IVA rate to CSV
                    transaction["debit"],
                    transaction["credit"],
                    transaction["balance"]
                ])
        messagebox.showinfo("Éxito", f"Historial exportado a {file_path}")

    def clear_history(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres limpiar el historial de transacciones?"):
            self.transactions = []
            self.update_transaction_table()
            self.disable_history_buttons() # Disable Edit/Delete buttons after clearing
            messagebox.showinfo("Información", "Historial de transacciones limpiado.")

    def select_transaction(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.selected_transaction_index = self.tree.index(row_id) # Get index of selected item
            self.enable_history_buttons() # Enable Edit/Delete buttons when a row is selected
        else:
            self.disable_history_buttons() # Disable buttons if no row is selected

    def enable_history_buttons(self):
        self.edit_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)

    def disable_history_buttons(self):
        self.edit_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.tree.selection_remove(self.tree.selection()) # Deselect any selected row

    def delete_transaction(self):
        if self.selected_transaction_index is not None:
            if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar este registro?"):
                del self.transactions[self.selected_transaction_index]
                self.update_transaction_table()
                self.disable_history_buttons() # Disable buttons after deletion
                self.selected_transaction_index = None # Reset selected index
                messagebox.showinfo("Información", "Registro eliminado del historial.")
        else:
            messagebox.showinfo("Advertencia", "Por favor, selecciona un registro para eliminar.")

    def edit_transaction(self):
        if self.selected_transaction_index is not None:
            selected_transaction = self.transactions[self.selected_transaction_index]
            EditTransactionDialog(self.root, selected_transaction, self.selected_transaction_index, self.update_transaction)
        else:
            messagebox.showinfo("Advertencia", "Por favor, selecciona un registro para editar.")

    def update_transaction(self, index, updated_transaction_data):
        self.transactions[index] = updated_transaction_data
        self.update_transaction_table()
        messagebox.showinfo("Información", "Registro del historial actualizado.")


class EditTransactionDialog(tk.Toplevel):
    def __init__(self, parent, transaction_data, transaction_index, update_callback):
        super().__init__(parent)
        self.title("Editar Registro de Transacción")
        self.transient(parent) # Dialog is modal over parent
        self.grab_set() # Take over user input

        self.transaction_index = transaction_index
        self.update_callback = update_callback

        # Variables to hold entry values
        self.sales_var = tk.StringVar(value=transaction_data['sales'])
        self.purchases_var = tk.StringVar(value=transaction_data['purchases'])
        self.iva_rate_var = tk.DoubleVar(value=transaction_data['iva_rate'])

        # Create form
        ttk.Label(self, text="Ventas Gravadas:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.sales_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Compras Gravadas:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.purchases_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Tasa de IVA (%):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.iva_rate_var).grid(row=2, column=1, padx=5, pady=5)

        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        save_button = ttk.Button(button_frame, text="Guardar", command=self.save_changes, style='Calculate.TButton')
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.cancel_edit, style='Clear.TButton')
        cancel_button.pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.cancel_edit) # Handle window close button
        self.wait_window(self) # Wait for dialog to close


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
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Date updated on edit
            "sales": round(updated_sales, 2),
            "purchases": round(updated_purchases, 2),
            "iva_rate": updated_iva_rate,
            "debit": round(debit, 2),
            "credit": round(credit, 2),
            "balance": round(balance_result, 2),
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
