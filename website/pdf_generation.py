import jinja2
import pdfkit

template_directory = "/home/wuukaa/Documents/GitHub/Etat-des-lieux-AGRAML/website/templates/edl"
output_directory = "/home/wuukaa/Documents/GitHub/Etat-des-lieux-AGRAML/storage/pdf/"
id = 50
context={"mes infos ici" : ''}

template_loader = jinja2.FileSystemLoader(template_directory)
template_env = jinja2.Environment(loader=template_loader)

template = template_env.get_template("pdf_edl_template.html")
output_html = template.render(context)

config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
pdf_file = pdfkit.from_string(output_html, output_directory + f'etat_des_lieux_{id}.pdf', configuration=config)
