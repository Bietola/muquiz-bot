\version "2.22.0"

% Utility functions
% showBarNums = \override Score.BarNumber.break-visibility = ##(#t #t #t)
% silenceMidi = \set Staff.midiMaximumVolume = #0
% wrong = \override NoteHead.color = #red

% Parts of the score
upper = \relative c'' {
  \clef treble
  \key c \major
  \time 4/4

  <c, e g c>2 <f a d f> <g b d g> <c, e g c>
}

lower = \relative c {
  \clef bass
  \key c \major
  \time 4/4

  <c, c'> <f f'> <g g'> <c, c'>
}

% Score
\score {
    % Bass
    \new PianoStaff \with { 
      instrumentName = "Piano" 
    } {
      <<
        \new Staff = "upper" \upper
        \new Staff = "lower" \lower
      >>
    }

  \layout { }

  \midi {
    \tempo 4 = 128
  }
}
