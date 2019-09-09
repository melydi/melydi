
  \version "2.16.2"
  \language "english"
  
  notes= {
   c,4. e,8 g,4 c4 a4 c8 a8 g,2 e,4 g,4 d,4 g,8 e,8 c,4 c,4 c,4
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
  