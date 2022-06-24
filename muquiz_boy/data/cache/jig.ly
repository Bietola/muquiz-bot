\version "2.22.2"
\language "english"
\score
{
    \layout {}
    \midi
    {
        \tempo 4 = 128
    }
    \new Score
    <<
        \new PianoStaff
        <<
            \new Staff
            {
                \new Voice
                {
                    {
                        <c e g c'>4
                        <f a d' f'>4
                        <g b d' g'>4
                        <c e g c'>4
                    }
                }
            }
            \new Staff
            {
                \new Voice
                {
                    {
                        c,4
                        f,4
                        g,4
                        c,4
                    }
                }
            }
        >>
    >>
}
