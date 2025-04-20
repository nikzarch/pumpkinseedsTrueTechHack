from fpdf import FPDF


def create_delivery_document(
        value: int,
        doc_number: str,
        doc_date: str,
        supplier: dict,
        buyer: dict,
        delivery_date: str,
        goods: list,
        output_filename: str = "delivery_document.pdf",
):
    pdf = FPDF()
    pdf.add_page()

    pdf.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSansCondensed-Bold.ttf", uni=True)

    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, "Документ поставки", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("DejaVu", "", 12)
    doc_number_str = f"№ {doc_number}    от ___________"
    pdf.cell(0, 10, doc_number_str, ln=True, align="C")
    pdf.ln(12)

    start_y = pdf.get_y()
    col_width = 85
    line_height = 7

    pdf.set_font("DejaVu", "B", 12)
    pdf.set_xy(10, start_y)
    pdf.cell(col_width, line_height, "Поставщик:", ln=2)
    pdf.set_font("DejaVu", "", 12)
    pdf.set_x(10)
    pdf.multi_cell(col_width, line_height,
                   f"{supplier['name']}\nТелефон: {supplier['phone']}\nEmail: {supplier['email']}", align="L")

    pdf.set_font("DejaVu", "B", 12)
    pdf.set_xy(110, start_y)
    pdf.cell(col_width, line_height, "Покупатель:", ln=2)
    pdf.set_font("DejaVu", "", 12)
    pdf.set_x(110)
    pdf.multi_cell(col_width, line_height, f"{buyer['name']}\nТелефон: {buyer['phone']}\nEmail: {buyer['email']}",
                   align="L")

    pdf.set_y(start_y + 30)
    pdf.ln(10)

    pdf.cell(0, 10, f"Срок поставки: ___________________", ln=True)
    pdf.ln(12)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Перечень товаров:", ln=True)
    pdf.ln(5)

    col_width_table = [pdf.w * 0.4, pdf.w * 0.25, pdf.w * 0.25]
    pdf.cell(col_width_table[0], 10, "Наименование товара", border=1)
    pdf.cell(col_width_table[1], 10, "Количество", border=1)
    pdf.cell(col_width_table[2], 10, "Цена", border=1, ln=True)

    pdf.set_font("DejaVu", "", 12)
    total_value = 0  # Инициализация итоговой суммы
    for item in goods:
        pdf.cell(col_width_table[0], 10, item["name"], border=1)
        pdf.cell(col_width_table[1], 10, str(item["quantity"]), border=1)
        pdf.cell(col_width_table[2], 10, str(item["price"]), border=1, ln=True)
        # Подсчет итоговой стоимости
        total_value += float(item["price"]) * float(item["quantity"])

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(col_width_table[0] + col_width_table[1], 10, "Итоговая стоимость:", border=1)
    pdf.cell(col_width_table[2], 10, f"{total_value:.2f}", border=1, ln=True)

    pdf.ln(20)

    start_y_sign = pdf.get_y()

    pdf.set_font("DejaVu", "B", 12)
    sign_col_width = 80
    vertical_padding = 5

    text_buyer = "Ответственное лицо Покупателя:"
    pdf.set_xy(10, start_y_sign)
    pdf.cell(sign_col_width, 10, text_buyer, ln=2)

    pdf.ln(vertical_padding + 3)
    line_length = pdf.get_string_width(text_buyer)
    pdf.line(10, pdf.get_y(), 10 + line_length, pdf.get_y())

    pdf.set_font("DejaVu", "", 12)
    pdf.cell(sign_col_width, 10, "(ФИО, подпись)", ln=True)

    text_supplier = "Ответственное лицо Поставщика:"
    pdf.set_font("DejaVu", "B", 12)
    pdf.set_xy(pdf.w - sign_col_width - 10, start_y_sign)
    pdf.cell(sign_col_width, 10, text_supplier, ln=2, align="R")

    pdf.ln(vertical_padding + 3)
    line_length = pdf.get_string_width(text_supplier)
    pdf.line(pdf.w - line_length - 10, pdf.get_y(), pdf.w - 10, pdf.get_y())

    pdf.set_font("DejaVu", "", 12)
    pdf.set_x(pdf.w - sign_col_width - 10)
    pdf.cell(sign_col_width, 10, "(ФИО, подпись)", ln=True, align="R")

    pdf.output(output_filename)