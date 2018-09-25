%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% iaf-iac.cls, v0.0, 2018-09-24
% Developed by Matt Vernacchia, mvernacc@mit.edu
%
% This class file enables authors to prepare papers
% according to the manuscript style requested by the
% International Astronautical Federation (IAF) for
% submissions to the International Astronautical
% Congress (IAC)
%
% This file is based on:
% new-aiaa.cls, v1.2, 2018/01/10
% Developed by Overleaf
%
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
\ProvidesClass{iaf-iac}[2018/09/24, v0.0]

\LoadClass[10pt]{article}

\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{microtype}
\RequirePackage{newtxtext,newtxmath}

\RequirePackage[letterpaper,margin=1in]{geometry}
\RequirePackage{enumitem}
\setlist{labelindent=\parindent,leftmargin=*,nosep}
\setlist[enumerate]{label={\arabic*)}}

\RequirePackage[symbol*]{footmisc}

\RequirePackage{setspace}

\RequirePackage[style]{abstract}
\renewcommand{\abstitlestyle}[1]{}
\renewcommand{\abstracttextfont}{\bfseries\normalsize}
\setlength{\absleftindent}{0.5in}
\setlength{\absrightindent}{0.5in}


\RequirePackage[blocks]{authblk}
\renewcommand{\Authfont}{\normalsize\upshape}
\renewcommand{\Affilfont}{\normalsize\itshape}
\setlength{\affilsep}{0pt}

\renewcommand{\maketitle}{%
  \begingroup
  \renewcommand\and{\\[\baselineskip]}
  \centering\singlespacing
  {\LARGE\bfseries\@title\par}
  \vskip2\baselineskip
  \@author\par
  \endgroup
  \vskip\baselineskip
  \setcounter{footnote}{0}
}


\RequirePackage[explicit]{titlesec}
\renewcommand{\thesection}{\arabic{section}}
\renewcommand{\thesubsection}{\thesection.\arabic{subsection}}
\renewcommand{\thesubsubsection}{\thesubsection.\arabic{subsubsection}}
\titleformat{\section}
  {\large\bfseries\singlespacing\centering}
  {\thesection.\space}{0pt}{#1}[]
\titlespacing{\section}{0pt}{0.5\baselineskip}{0pt}
\titleformat{\subsection}
  {\normalsize\bfseries\singlespacing}
  {\thesection.\arabic{subsection}.\space}{0pt}{#1}[]
\titlespacing{\subsection}{0pt}{0.5\baselineskip}{0pt}
\titleformat{\subsubsection}
  {\normalsize\itshape\singlespacing}
  {\thesection.\thesubsection.\arabic{subsubsection}.\space}{0pt}{#1}[]
\titlespacing{\subsubsection}{0pt}{0.5\baselineskip}{0pt}

\RequirePackage{lettrine}
\setlength{\DefaultNindent}{0pt}

\RequirePackage[tableposition=top]{caption}
\renewcommand{\figurename}{Fig.}
\captionsetup*{labelsep=quad}
\renewcommand{\arraystretch}{1.2}

\RequirePackage[indentfirst=false,font+=small,leftmargin=0.4in,rightmargin=0pt,vskip=0pt]
{quoting}

\setlength{\abovedisplayskip}{\baselineskip}
\setlength{\belowdisplayskip}{\baselineskip}
\setlength{\abovedisplayshortskip}{\baselineskip}
\setlength{\belowdisplayshortskip}{\baselineskip}

\RequirePackage[sort&compress,numbers]{natbib}
\bibliographystyle{new-aiaa}
\renewcommand{\bibfont}{\small}

\RequirePackage[hyphens]{url}
\RequirePackage{hyperref}
