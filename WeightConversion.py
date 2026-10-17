# Comprehensive Weight Converter (Tkinter)

from tkinter import *

# Conversion factors relative to Grams (base unit)
UNITS = {
    "Milligram (mg)": 0.001,
    "Gram (g)": 1.0,
    "Kilogram (kg)": 1000.0,
    "Metric Ton (t)": 1000000.0,
    "Ounce (oz)": 28.349527,
    "Pound (lb)": 453.59237,
    "Stone (st)": 6350.29318
}

def convert():
    try:
        # Get input value and selected unit
        val = float(entry_val.get())
        selected_unit = input_unit_var.get()
        
        # Convert input to base unit (grams)
        grams_value = val * UNITS[selected_unit]
        
        # Clear previous results
        result_text.delete("1.0", END)
        
        # Calculate and display conversions for all units
        results = []
        for unit_name, factor in UNITS.items():
            converted_val = grams_value / factor
            results.append(f"{unit_name}: {converted_val:,.6g}\n")
            
        result_text.insert(END, "".join(results))
        
    except ValueError:
        result_text.delete("1.0", END)
        result_text.insert(END, "Error: Please enter a valid number!")

# Main program window
if __name__ == '__main__':
    root = Tk()
    root.title('Universal Weight Converter')
    root.geometry('420x400')
    root.config(bg='#f0f0f0')

    # Title Label
    title_label = Label(root, text='⚖️ Weight Converter', font=('Arial', 14, 'bold'), bg='#f0f0f0', fg='#333')
    title_label.pack(pady=10)

    # Input Frame
    input_frame = Frame(root, bg='#f0f0f0')
    input_frame.pack(pady=5)

    Label(input_frame, text='Enter Weight:', font=('Arial', 10), bg='#f0f0f0').pack(side=LEFT, padx=5)
    
    entry_val = StringVar()
    entry_box = Entry(input_frame, textvariable=entry_val, width=12, font=('Arial', 11))
    entry_box.pack(side=LEFT, padx=5)

    # Dropdown for selecting input unit
    input_unit_var = StringVar(root)
    input_unit_var.set("Kilogram (kg)")  # default value
    
    unit_menu = OptionMenu(input_frame, input_unit_var, *UNITS.keys())
    unit_menu.config(font=('Arial', 9), width=14)
    unit_menu.pack(side=LEFT, padx=5)

    # Convert Button
    btn_convert = Button(root, text='Convert to All Units', command=convert, font=('Arial', 10, 'bold'), bg='#667eea', fg='white', padx=10, pady=5)
    btn_convert.pack(pady=15)

    # Output Display Area (Text widget with scrollbar support capability)
    result_frame = Frame(root)
    result_frame.pack(pady=5)

    result_text = Text(result_frame, height=10, width=38, font=('Courier', 10))
    result_text.pack(side=LEFT, fill=BOTH)

    root.mainloop()