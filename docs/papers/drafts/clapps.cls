%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%  clapps.cls --- Praxia / Kontablo open-access paper class
%  ("Christian Luciani APPlied Standards" house style)
%
%  A clean-room house style for Praxia research preprints and standards
%  documents. Article-based. Depends only on packages that ship with every
%  TeX Live / MiKTeX base install (xcolor, hyperref, geometry, lmodern,
%  microtype); every nicer package (lexend, titlesec, epigraph, tcolorbox)
%  is used opportunistically *if present* and degrades gracefully if not, so
%  the document always compiles with pdflatex and no engine switch.
%
%  House identity:
%    - Lexend typography when available (dyslexia-friendly humanist sans),
%      with a graceful Latin Modern fallback.
%    - A restrained two-colour palette (deep slate ink + teal accent),
%      deliberately distinct from any institutional template.
%    - Sans-serif, accent-coloured section headings and title block.
%    - A dual-readership convention: a machine-readable summary path and a
%      human reading path, supported by \summarynote and \clappsepigraph.
%
%  Written from scratch. Inspired by the layout ideas of common open-access
%  report templates but copying no code from any of them; carries no
%  third-party licensing obligation.
%
%  Licence: LaTeX Project Public License (LPPL) 1.3c or later.
%  Author:  Christian Luciani / Praxia.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{clapps}[2026/06/16 v1.0 Praxia/Kontablo house style]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[a4paper]{article}

% --- Page geometry -----------------------------------------------------------
\RequirePackage[a4paper, margin=1in]{geometry}

% --- Typography (always-present base; Lexend if installed) -------------------
\RequirePackage{lmodern}
\RequirePackage[T1]{fontenc}
\RequirePackage{microtype}

\newif\ifclapps@lexend
\IfFileExists{lexend.sty}{\clapps@lexendtrue}{\clapps@lexendfalse}
\ifclapps@lexend
  \RequirePackage{lexend}
  \renewcommand{\familydefault}{\sfdefault}% Lexend everywhere (body + headings)
\else
  \ClassWarningNoLine{clapps}{Package `lexend' not found --- falling back to
    Latin Modern. Run `tlmgr install lexend' for the full Praxia typography.}%
\fi

% --- Colour palette (subtle, two-colour) -------------------------------------
\RequirePackage{xcolor}
\definecolor{clappsInk}{HTML}{1F2933}    % deep slate, near-black body ink
\definecolor{clappsAccent}{HTML}{0E7C7B} % muted teal, headings & rules
\definecolor{clappsMuted}{HTML}{52606D}  % secondary grey for meta lines

% --- Section headings (titlesec if present, else base \@startsection) --------
\IfFileExists{titlesec.sty}{%
  \RequirePackage{titlesec}%
  \titleformat{\section}
    {\sffamily\Large\bfseries\color{clappsAccent}}{\color{clappsAccent}\thesection}{0.7em}{}%
  \titleformat{\subsection}
    {\sffamily\large\bfseries\color{clappsInk}}{\color{clappsAccent}\thesubsection}{0.6em}{}%
  \titleformat{\subsubsection}
    {\sffamily\normalsize\bfseries\color{clappsInk}}{\color{clappsAccent}\thesubsubsection}{0.5em}{}%
}{%
  % Base-LaTeX fallback: the final argument of \@startsection styles the whole
  % heading (number included), giving sans + accent headings with no package.
  \renewcommand\section{\@startsection{section}{1}{\z@}%
     {-3.5ex \@plus -1ex \@minus -.2ex}{2.3ex \@plus.2ex}%
     {\sffamily\Large\bfseries\color{clappsAccent}}}%
  \renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
     {-3.25ex\@plus -1ex \@minus -.2ex}{1.5ex \@plus .2ex}%
     {\sffamily\large\bfseries\color{clappsInk}}}%
  \renewcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%
     {-3.25ex\@plus -1ex \@minus -.2ex}{1.5ex \@plus .2ex}%
     {\sffamily\normalsize\bfseries\color{clappsInk}}}%
}

% --- Title block (base \@maketitle override; no titling dependency) ----------
\renewcommand{\maketitle}{%
  \newpage\thispagestyle{plain}\null\vskip 2em%
  \begin{center}%
    {\sffamily\LARGE\bfseries\color{clappsInk}\@title \par}%
    \vskip 0.5em{\color{clappsAccent}\rule{0.18\textwidth}{1.2pt}}\par
    \vskip 1em{\sffamily\large\color{clappsInk}\@author \par}%
    \vskip 1em{\sffamily\small\color{clappsMuted}\@date \par}%
  \end{center}\par
  \@thanks
  \vskip 1.5em%
  \setcounter{footnote}{0}%
  \global\let\thanks\relax%
  \global\let\maketitle\relax}

% --- Links -------------------------------------------------------------------
\RequirePackage[colorlinks=true, allcolors=clappsAccent, breaklinks=true]{hyperref}

% --- Epigraph (recurring motif): use package if present, else minimal macro --
% Note: definitions with #-parameters must live outside the \IfFileExists
% argument (where # is illegal); we branch on a boolean instead.
\newif\ifclapps@epigraph
\IfFileExists{epigraph.sty}{\clapps@epigraphtrue}{\clapps@epigraphfalse}
\ifclapps@epigraph
  \RequirePackage{epigraph}
  \setlength{\epigraphwidth}{0.55\textwidth}
  \renewcommand{\epigraphflush}{center}
  \newcommand{\clappsepigraph}[2]{\epigraph{#1}{#2}}
\else
  \newcommand{\clappsepigraph}[2]{%
    \begin{center}\begin{minipage}{0.6\textwidth}\raggedleft\small\itshape
      #1\par\vskip0.3em\upshape\normalfont\footnotesize\color{clappsMuted}--- #2
    \end{minipage}\end{center}\vskip1em}
\fi

% --- Dual-readership block: tcolorbox if present, else plain framed box -------
\newif\ifclapps@tcb
\IfFileExists{tcolorbox.sty}{\clapps@tcbtrue}{\clapps@tcbfalse}
\ifclapps@tcb
  \RequirePackage[most]{tcolorbox}
  \newtcolorbox{summarynote}{%
    colback=clappsAccent!4, colframe=clappsAccent!55, boxrule=0.6pt, arc=2pt,
    left=8pt, right=8pt, top=6pt, bottom=6pt}
\else
  \newenvironment{summarynote}{%
    \par\vskip0.5em\noindent
    \begin{minipage}{\dimexpr\linewidth-2\fboxsep-2\fboxrule}%
    \color{clappsAccent}\rule{\linewidth}{0.6pt}\par\vskip4pt\color{black}%
  }{%
    \par\vskip4pt\color{clappsAccent}\rule{\linewidth}{0.6pt}%
    \end{minipage}\par\vskip0.5em}
\fi

% --- Compact, sections-only contents for the abstract page -------------------
\newcommand{\compactcontents}{%
  \begingroup
  \setcounter{tocdepth}{1}%
  \renewcommand{\contentsname}{\normalsize\sffamily\color{clappsInk}Contents}%
  {\small\parskip=-2pt\tableofcontents}%
  \endgroup}

\endinput
