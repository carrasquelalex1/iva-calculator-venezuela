import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import csv
from datetime import datetime
from ttkthemes import ThemedTk  # Import ThemedTk

class AdvancedIVACalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de IVA Venezuela")  # More concise title
        # self.root.geometry("800x600") # Remove fixed geometry, let it expand

        # Variables de estado
        self.sales = tk.StringVar()
        self.purchases = tk.StringVar()
        self.iva_rate = tk.DoubleVar(value=16.0) # Default IVA rate as per website
        self.credit_fiscal = tk.DoubleVar()
        self.debit_fiscal = tk.DoubleVar()
        self.balance = tk.DoubleVar()
        self.transactions = []
        self.selected_transaction_index = None # To keep track of selected row index

        # Estilo ttk con colores personalizados (Adjusted for website feel - optional)
        self.style = ttk.Style(root)

        # --- Estilos de Botones --- (Slightly adjusted button styles for cleaner look)
        self.style.configure('TButton', font=('Arial', 10), padding=8) # Slightly larger padding
        self.style.configure('Calculate.TButton', background='#007bff', foreground='white', relief='flat') # Blue Calculate - Bootstrap style
        self.style.map('Calculate.TButton', background=[('active', '#0056b3')]) # Darker blue on active
        self.style.configure('Export.TButton', background='#28a745', foreground='white', relief='flat') # Green Export - Bootstrap style
        self.style.map('Export.TButton', background=[('active', '#1e7e34')]) # Darker green on active
        self.style.configure('Clear.TButton', background='#dc3545', foreground='white', relief='flat') # Red Clear - Bootstrap style
        self.style.map('Clear.TButton', background=[('active', '#bd2130')]) # Darker red on active
        self.style.configure('Edit.TButton', background='#ffc107', foreground='black', relief='flat') # Yellow Edit - Bootstrap style
        self.style.map('Edit.TButton', background=[('active', '#ffb300')]) # Darker yellow on active
        self.style.configure('Delete.TButton', background='#6c757d', foreground='white', relief='flat') # Gray Delete - Bootstrap style
        self.style.map('Delete.TButton', background=[('active', '#5a6268')]) # Darker gray on active


        # Diseño de la interfaz
        self.create_widgets()

    def create_widgets(self):
        # Título
        title_label = ttk.Label(self.root, text="Calculadora de IVA Venezuela", font=("Arial", 18, "bold")) # Bolder title
        title_label.pack(pady=20)

        # Entradas
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill=tk.X) # Add padx and fill for better spacing

        ttk.Label(input_frame, text="Ventas Gravadas (Bs.S):", width=20, anchor='w').grid(row=0, column=0, padx=5, pady=5, sticky="ew") # More descriptive label, fixed width
        sales_entry = ttk.Entry(input_frame, textvariable=self.sales)
        sales_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        sales_entry.focus() # Focus on sales entry on startup

        ttk.Label(input_frame, text="Compras Gravadas (Bs.S):", width=20, anchor='w').grid(row=1, column=0, padx=5, pady=5, sticky="ew") # More descriptive label, fixed width
        ttk.Entry(input_frame, textvariable=self.purchases).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Tasa de IVA (%):", width=20, anchor='w').grid(row=2, column=0, padx=5, pady=5, sticky="ew") # Fixed width
        iva_rate_entry = ttk.Entry(input_frame, textvariable=self.iva_rate, width=10) # Smaller width for rate entry
        iva_rate_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w") # Sticky west to align left
        ttk.Label(input_frame, text="%", anchor='w').grid(row=2, column=2, padx=0, pady=5, sticky="w") # Percent symbol

        input_frame.columnconfigure(1, weight=1) # Make entry columns expandable

        # Frame para botón de cálculo
        calculate_frame = ttk.Frame(self.root)
        calculate_frame.pack(pady=10)
        calculate_button = ttk.Button(calculate_frame, text="Calcular IVA", command=self.calculate_balance, style='Calculate.TButton') # Simpler button text
        calculate_button.pack(pady=5)

        # Resultados
        results_frame = ttk.Frame(self.root)
        results_frame.pack(pady=10, padx=20, fill=tk.X) # Add padx and fill for better spacing

        ttk.Label(results_frame, text="Débito Fiscal (IVA Cobrado):", width=30, anchor='w').grid(row=0, column=0, padx=5, pady=5, sticky="ew") # Wider label
        ttk.Label(results_frame, textvariable=self.debit_fiscal).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(results_frame, text="Crédito Fiscal (IVA Pagado):", width=30, anchor='w').grid(row=1, column=0, padx=5, pady=5, sticky="ew") # Wider label
        ttk.Label(results_frame, textvariable=self.credit_fiscal).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(results_frame, text="Total IVA a Pagar/Devolver:", width=30, anchor='w', font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, pady=5, sticky="ew") # Bold for emphasis, more descriptive
        ttk.Label(results_frame, textvariable=self.balance, font=("Arial", 10, "bold")).grid(row=2, column=1, padx=5, pady=5, sticky="ew") # Bold balance

        results_frame.columnconfigure(1, weight=1) # Make result columns expandable


        # Historial de transacciones
        history_frame = ttk.Frame(self.root)
        history_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True) # Fill and expand history frame

        ttk.Label(history_frame, text="Historial de Transacciones", font=("Arial", 14, "bold")).pack(pady=(0,5), anchor='w') # Bolder history title

        self.tree = ttk.Treeview(history_frame, columns=("Fecha", "Ventas", "Compras", "Tasa IVA (%)", "Débito", "Crédito", "Saldo"), show="headings") # Added "Tasa IVA (%)"
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Ventas", text="Ventas (Bs.S)") # More descriptive headings
        self.tree.heading("Compras", text="Compras (Bs.S)") # More descriptive headings
        self.tree.heading("Tasa IVA (%)", text="Tasa IVA (%)") # Header for new column
        self.tree.heading("Débito", text="Débito Fiscal (Bs.S)") # More descriptive headings
        self.tree.heading("Crédito", text="Crédito Fiscal (Bs.S)") # More descriptive headings
        self.tree.heading("Saldo", text="Total IVA (Bs.S)") # More descriptive headings
        self.tree.pack(fill=tk.BOTH, expand=True) # Fill and expand treeview

        self.tree.bind("<ButtonRelease-1>", self.select_transaction) # Bind click event to select row

        # Frame for Edit/Delete/Export/Clear buttons (below history table)
        history_button_frame = ttk.Frame(history_frame)
        history_button_frame.pack(pady=5, fill=tk.X)

        self.edit_button = ttk.Button(history_button_frame, text="Editar", command=self.edit_transaction, style='Edit.TButton', state=tk.DISABLED) # Shorter button text
        self.edit_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X) # Expand buttons

        self.delete_button = ttk.Button(history_button_frame, text="Eliminar", command=self.delete_transaction, style='Delete.TButton', state=tk.DISABLED) # Shorter button text
        self.delete_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X) # Expand buttons

        export_button = ttk.Button(history_button_frame, text="Exportar a CSV", command=self.export_to_csv, style='Export.TButton') # Shorter button text
        export_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X) # Expand buttons

        clear_button = ttk.Button(history_button_frame, text="Limpiar Historial", command=self.clear_history, style='Clear.TButton')
        clear_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X) # Expand buttons

        history_button_frame.columnconfigure(0, weight=1) # Ensure buttons expand to fill space
        history_button_frame.columnconfigure(1, weight=1)
        history_button_frame.columnconfigure(2, weight=1)
        history_button_frame.columnconfigure(3, weight=1)


        # Label de agradecimiento al final (Removed for cleaner look - can be added back if desired)
        # footer_label = ttk.Label(self.root, text="Creado por Alexander Carrasquel. Agradecer no cuesta nada. https://www.linkedin.com/in/alexander-carrasquel-41a616108/", font=("Arial", 8))
        # footer_label.pack(pady=5, side=tk.BOTTOM) # Pack al final y abajo


    def calculate_balance(self):
        try:
            sales_amount = float(self.sales.get())
            purchases_amount = float(self.purchases.get())
            rate = float(self.iva_rate.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos.")
            return

        debit = (sales_amount * rate) / 100
        credit = (purchases_amount * rate) / 100
        balance_result = debit - credit

        self.debit_fiscal.set(f"{debit:,.2f}") # Format with comma separator and 2 decimals
        self.credit_fiscal.set(f"{credit:,.2f}") # Format with comma separator and 2 decimals
        self.balance.set(f"{balance_result:,.2f}") # Format with comma separator and 2 decimals

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
                f"{transaction['sales']:,.2f}", # Format with comma
                f"{transaction['purchases']:,.2f}", # Format with comma
                transaction["iva_rate"], # Displaying IVA rate in the table
                f"{transaction['debit']:,.2f}", # Format with comma
                f"{transaction['credit']:,.2f}", # Format with comma
                f"{transaction['balance']:,.2f}" # Format with comma
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
        self.title("Editar Registro") # Shorter title
        self.transient(parent) # Dialog is modal over parent
        self.grab_set() # Take over user input

        self.transaction_index = transaction_index
        self.update_callback = update_callback

        # Variables to hold entry values
        self.sales_var = tk.StringVar(value=transaction_data['sales'])
        self.purchases_var = tk.StringVar(value=transaction_data['purchases'])
        self.iva_rate_var = tk.DoubleVar(value=transaction_data['iva_rate'])

        # Create form
        ttk.Label(self, text="Ventas Gravadas (Bs.S):").grid(row=0, column=0, padx=5, pady=5, sticky="w") # More descriptive label
        ttk.Entry(self, textvariable=self.sales_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Compras Gravadas (Bs.S):").grid(row=1, column=0, padx=5, pady=5, sticky="w") # More descriptive label
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
