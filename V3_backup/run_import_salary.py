from salary_import_tool import import_salary_pdf

if __name__ == "__main__":
    pdf_path = r"C:\DEV\PayDay\DEV\V3\SQL\x\Abrechnungen\Abrechnungen 07_2025.pdf"
    result = import_salary_pdf(pdf_path)
    print(result)

