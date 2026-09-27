# Compilacao da monografia: pdflatex + bibtex (abntex2cite), auxiliares em build/.
# Usado pelo build.ps1 e pelo LaTeX Workshop (VS Code); rode a partir desta pasta.
$pdf_mode = 1;
$bibtex_use = 2;
$out_dir = 'build';
$pdflatex = 'pdflatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
# O bibtex roda dentro de build/; sem isto ele nao acha o .bib da raiz.
$ENV{'BIBINPUTS'} = '..;' . ($ENV{'BIBINPUTS'} // '');
@default_files = ('tcc.tex');
