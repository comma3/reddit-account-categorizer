strings will be matched with .lower(), so no capitals

// avoids e.g., was a man who, etc.
[!w]as a man 
[!w]as a male
[!w]as a boy
[!w]as a father
[!w]as a brother
 
// i[a' ]{0,2}m = im i'm i am
// need to include im to avoid e.g., she was not a woman
i[a' ]{0,2}m a man
i[a' ]{0,2}m a male
i[a' ]{0,2}m a boy

i[a' ]{0,2}m not a woman 
i[a' ]{0,2}m not a female
i[a' ]{0,2}m not a girl
i[a' ]{0,2}m not a mother

// age/sex/location
[0-9]\/m([ .,:;\/\)]|ale)  //only m, male, or punctuation




