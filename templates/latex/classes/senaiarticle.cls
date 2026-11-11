\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{senaiarticle}[2026/11/11 v0.1 Classe neutra do primeiro MVP]

\LoadClass[11pt,a4paper]{article}

% A identidade visual definitiva será aplicada em uma etapa posterior.
% Esta classe cuida apenas de legibilidade, estrutura e blocos semânticos.
\RequirePackage{fontspec}
\defaultfontfeatures{Ligatures=TeX}
\IfFontExistsTF{TeX Gyre Heros}{
  \setsansfont{TeX Gyre Heros}
}{
  \setsansfont{Arial}
}
\renewcommand{\familydefault}{\sfdefault}

\RequirePackage[a4paper,margin=2.5cm]{geometry}
\RequirePackage{xcolor}
\RequirePackage[most]{tcolorbox}
\RequirePackage{booktabs}
\RequirePackage{longtable}
\RequirePackage{graphicx}
\RequirePackage{microtype}
\RequirePackage{hyperref}

\definecolor{senaiAzulNeutro}{HTML}{244A64}
\definecolor{senaiCinzaClaro}{HTML}{F3F5F6}
\definecolor{senaiVermelhoNeutro}{HTML}{8A2E2E}
\definecolor{senaiVerdeNeutro}{HTML}{2F6549}

\hypersetup{
  colorlinks=true,
  linkcolor=senaiAzulNeutro,
  urlcolor=senaiAzulNeutro,
  citecolor=senaiAzulNeutro
}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55em}
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{3}

\newtcolorbox{senaiobjetivo}{
  enhanced,breakable,title={Objetivo de aprendizagem},
  colback=senaiCinzaClaro,colframe=senaiAzulNeutro,fonttitle=\bfseries
}
\newtcolorbox{senaisituacao}{
  enhanced,breakable,title={Situação-problema},
  colback=senaiCinzaClaro,colframe=senaiAzulNeutro,fonttitle=\bfseries
}
\newtcolorbox{senaiquestao}[1][]{
  enhanced,breakable,title={Questão #1},
  colback=white,colframe=senaiAzulNeutro,fonttitle=\bfseries
}
\newtcolorbox{senaiseguranca}{
  enhanced,breakable,title={Segurança},
  colback=red!3,colframe=senaiVermelhoNeutro,fonttitle=\bfseries
}
\newtcolorbox{senairubrica}{
  enhanced,breakable,title={Critério de avaliação},
  colback=green!3,colframe=senaiVerdeNeutro,fonttitle=\bfseries
}
\newtcolorbox{senaipratica}{
  enhanced,breakable,title={Atividade prática},
  colback=green!3,colframe=senaiVerdeNeutro,fonttitle=\bfseries
}
\newtcolorbox{senaiatencao}{
  enhanced,breakable,title={Atenção},
  colback=red!3,colframe=senaiVermelhoNeutro,fonttitle=\bfseries
}

\AtBeginDocument{\raggedbottom}
