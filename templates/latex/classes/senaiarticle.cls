\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{senaiarticle}[2026/11/11 v0.2 Documentos e artigo institucional]

\newif\ifsenai@artigo
\DeclareOption{artigo}{\senai@artigotrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\ifsenai@artigo
  \LoadClass[12pt,a4paper]{article}
\else
  \LoadClass[11pt,a4paper]{article}
\fi

% O modo padrão preserva os documentos pedagógicos do primeiro MVP.
% A opção artigo aplica o perfil acadêmico da referência institucional.
\RequirePackage{fontspec}
\defaultfontfeatures{Ligatures=TeX}
\IfFontExistsTF{TeX Gyre Heros}{
  \setsansfont{TeX Gyre Heros}
}{
  \IfFontExistsTF{Liberation Sans}{\setsansfont{Liberation Sans}}{
    \IfFontExistsTF{Arial}{\setsansfont{Arial}}{
      \setsansfont{Latin Modern Sans}
    }
  }
}
\renewcommand{\familydefault}{\sfdefault}

\ifsenai@artigo
  \RequirePackage[a4paper,top=3cm,left=3cm,bottom=2cm,right=2cm]{geometry}
\else
  \RequirePackage[a4paper,margin=2.5cm]{geometry}
\fi
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

\ifsenai@artigo
  \IfFontExistsTF{Times New Roman}{\setmainfont{Times New Roman}}{
    \IfFontExistsTF{TeX Gyre Termes}{\setmainfont{TeX Gyre Termes}}{
      \IfFontExistsTF{Liberation Serif}{\setmainfont{Liberation Serif}}{
        \setmainfont{Latin Modern Roman}
      }
    }
  }
  \renewcommand{\familydefault}{\rmdefault}
  \RequirePackage{setspace}
  \RequirePackage{indentfirst}
  \RequirePackage{titlesec}
  \RequirePackage{fancyhdr}
  \onehalfspacing
  \setlength{\parindent}{1.25cm}
  \setlength{\parskip}{0pt}
  \setlength{\headheight}{15pt}
  \titleformat{\section}{\normalfont\normalsize\bfseries}
    {\thesection}{1em}{\MakeUppercase}
  \titleformat{name=\section,numberless}
    {\normalfont\normalsize\bfseries\centering}{}{0pt}{\MakeUppercase}
  \titleformat{\subsection}{\normalfont\normalsize\bfseries}
    {\thesubsection}{1em}{}
  \titleformat{\subsubsection}{\normalfont\normalsize}
    {\thesubsubsection}{1em}{}
  \titlespacing{\section}{0pt}{18pt}{18pt}
  \titlespacing{\subsection}{0pt}{18pt}{18pt}
  \titlespacing{\subsubsection}{0pt}{18pt}{18pt}
  \fancypagestyle{senaiartigo}{
    \fancyhf{}
    \fancyhead[R]{\normalfont\small\thepage}
    \renewcommand{\headrulewidth}{0pt}
    \renewcommand{\footrulewidth}{0pt}
  }
  \hypersetup{hidelinks,colorlinks=false}
  \widowpenalty=10000
  \clubpenalty=10000
\fi

\AtBeginDocument{\raggedbottom}
