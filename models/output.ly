
  \version "2.16.2"
  \language "english"
  
  notes= \relative c' {
  c4. e8 g4 c4 a4 c8 a8 g2 e4 g4 d4 g8 e8 c4 c4 c4
  \bar "|."
  }
  
  \score {

  \new PianoStaff << 
    \new Staff = "upper" { 
      \clef treble
      \notes
    } 
  >>
    \layout {
      #(layout-set-staff-size 25.2)
  \context {
        \Score
        \override SpacingSpanner
                  #'base-shortest-duration = #(ly:make-moment 1 16)
      }
    }
  }
  