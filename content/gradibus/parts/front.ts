import { one, paragraph, segment, type Chapter } from "../../schema";

export const retractatio: Chapter = {
  id: "retractatio",
  title: "Retractatio",
  heading: "Bernard’s correction of his own treatise",
  paragraphs: [
    one(
      "r1",
      "R.1",
      "In hoc opusculo, cum illud de Evangelio, quod Dominus ait, diem ultimi iudicii se nescire, ad aliquam sententiam confirmandam atque roborandam proferrem in medium, improvide quiddam apposui quod in Evangelio scriptum non esse postea deprehendi. Nam cum textus habeat tantummodo: Neque Filius scit (Marc. xiii, 32), ego deceptus magis quam fallere volens, litterae quippe immemor, sed non sensus: Nec ipse, inquam, Filius hominis scit.",
      "In order to strengthen and support a certain opinion expressed in this little book I quoted the passage in the Gospel in which Our Lord states that He was unaware of the date of the final Judgment. To this I inadvertently added a word which, as I have since discovered, does not occur in the Gospel. For the text has simply ‘neither the Son knoweth’, whereas I, thinking rather of the sense than of the wording, and with no intention to mislead, by mistake wrote: ‘The Son of Man Himself knoweth not.’",
      "In this little work, when I brought forward that saying of the Gospel, that the Lord said He did not know the day of the last judgment, to confirm and strengthen a certain opinion, I incautiously added something which I afterwards found is not written in the Gospel. For while the text has only: ‘Neither does the Son know,’ I — deceived rather than wishing to deceive, unmindful of the letter, but not of the sense — said: ‘Nor does the Son of man himself know.’",
      [
        {
          kind: "text",
          title: "The slip that organizes cap. III",
          body: "Bernard’s later argument in §§10–11 turns on Filius hominis. The retractatio admits the Gospel has only Filius. Mills keeps the English anecdote; the Latin is a confession about the letter (litterae immemor, sed non sensus).",
        },
      ],
    ),
    one(
      "r2",
      "R.2",
      "Vnde etiam totam ordiens sequentem disputationem ex eo quod non veraciter posui, veram conatus sum approbare assertionem. Sed quia talem errorem meum multo post, quam a me idem libellus editus et a pluribus iam transcriptus fuit, deprehendi, cum non potui per tot iam libellos sparsum persequi mendacium, necessarium credidi confugere ad confessionis remedium.",
      "On this I based the whole of the subsequent argument, in which I attempted to prove the truth of my assertion by means of an inaccurate quotation. I did not discover my mistake until long after the publication of the pamphlet, and when a number of copies had been made. It is impossible to correct a misstatement in a book which has had a wide circulation, so I have thought it incumbent on me to resort to the only possible remedy — an admission that I was wrong.",
      "Whence also, beginning the whole following disputation from what I did not truly set down, I tried to approve a true assertion. But because I detected this error of mine long after the same little book had been published by me and already copied by many, since I could not chase a falsehood already scattered through so many booklets, I thought it necessary to flee to the remedy of confession.",
    ),
    one(
      "r3",
      "R.3",
      "Alio quoque in loco quamdam de Seraphim opinionem posui, quam numquam audivi, nusquam legi. Vbi sane lector meus attendat, quod proinde temperanter puto dixerim, volens videlicet non aliud quam putari, quod certum reddere de Scripturis non valui.",
      "And in another passage I have expressed a definite opinion about the Seraphim which I never heard, and have nowhere read. Here also my readers may well consider that it would have been more reasonable on my part to have said ‘I suppose’, as I had certainly no desire to offer more than a conjecture on a matter which I was unable to prove from Scripture.",
      "In another place as well I set down a certain opinion about the Seraphim, which I have never heard, nowhere read. Here my reader should notice that I therefore said ‘I suppose’ temperately, wishing namely that nothing more be thought than a supposition, which I was not able to make certain from the Scriptures.",
    ),
    one(
      "r4",
      "R.4",
      "Titulus quoque ipse qui De gradibus humilitatis inscribitur, pro eo forsitan quod non humilitatis, sed superbiae potius hic distingui describique videntur gradus, calumniam patietur, sed hoc a minus vel intelligentibus, vel attendentibus eiusdem tituli rationem, quam tamen in fine opusculi ipse breviter intimare curavi.",
      "It is also possible that the title chosen ‘Concerning the Degrees of Humility’ may incur censure — but this will come only from those who overlook or misunderstand the meaning of that title — an explanation of which I have been careful to give in the conclusion of the tract.",
      "The title itself also, which is inscribed ‘On the degrees of humility,’ will perhaps suffer calumny, because here the degrees that seem to be distinguished and described are not those of humility but rather of pride — but this from those less either understanding, or attending to, the reason of the same title, which nevertheless I myself have taken care to intimate briefly at the end of the little work.",
    ),
  ],
};

export const preface: Chapter = {
  id: "praefatio",
  title: "Praefatio",
  heading: "To brother Godfrey",
  paragraphs: [
    paragraph("pref", undefined, [
      segment(
        "pref.1",
        "Rogasti me, frater Godefride, quatenus ea quae de gradibus humilitatis coram fratribus locutus fueram, pleniori tibi tractatu dissererem.",
        "You have asked me, brother Godfrey, to expand and put in writing the substance of the addresses ‘On the Degrees of Humility’ which I had delivered to the brethren.",
        "You asked me, brother Godfrey, that I should set forth to you, in a fuller treatise, those things which I had spoken before the brothers concerning the degrees of humility.",
      ),
      segment(
        "pref.2",
        "Cui tuae petitioni digne, ut dignum erat, et volens satisfacere, et timens non posse, evangelici consilii memor, non prius, fateor, incipere ausus sum, quam sedens computavi, si sufficerent sumptus ad perficiendum (Luc. xiv, 28).",
        "I admit that, anxious as I was to give to this request of yours the serious answer that it deserved, I was doubtful whether I could comply with it. For with the evangelist’s warning in my mind, I did not venture to begin the work, until I had sat down and calculated whether my resources were sufficient for its completion.",
        "To which petition of yours, as was worthy, both wishing to satisfy and fearing not to be able, mindful of the evangelical counsel, I confess I did not dare to begin before, sitting down, I counted whether the costs would suffice for finishing.",
      ),
      segment(
        "pref.3",
        "Cum autem charitas hunc foras misisset timorem, quo mihi timebam illudi de opere non consummando, subintravit alius timor de contrario, quo coepi timere gravius periculum de gloria si perfecissem, quam de ignominia si defecissem.",
        "Then, when love had cast out the fear that I had entertained of ridicule for failure to complete my work, it was replaced by misgiving of a different kind; for I was apprehensive of greater danger from the credit that might attend success than of the disgrace that might attach to failure.",
        "But when charity had cast this fear outside — the fear by which I feared to be mocked for a work not finished — another fear from the contrary slipped in, by which I began to fear a graver danger from glory if I should have finished, than from ignominy if I should have failed.",
        [
          {
            kind: "word",
            title: "charitas, not ‘love’ only",
            body: "Bernard writes charitas (the fear-casting charity of 1 Jn 4:18). Mills says ‘love’. The close line keeps charity so the biblical echo stays audible.",
          },
        ],
      ),
      segment(
        "pref.4",
        "Vnde inter hunc timorem et charitatem, velut in quodam bivio positus, diu haesitavi, cui viarum tuto me crederem; metuens aut loquendo utiliter de humilitate, ipse humilis non inveniri; aut tacendo humiliter, inutilis fieri.",
        "So I found myself, as it were, at the parting of the ways indicated respectively by affection and by fear; and I was long in doubt as to which was the safer choice. For I was afraid that if I said anything worth saying about humility, I might myself be found wanting in that virtue, whereas if, on grounds of modesty, I refused to speak, I might fail in usefulness.",
        "Whence between this fear and charity, placed as if at a certain fork, I hesitated long, to which of the ways I might safely commit myself; fearing either, by speaking usefully of humility, not to be found humble myself; or, by being silent humbly, to become useless.",
      ),
      segment(
        "pref.5",
        "Cumque neutram tutam, alterutram tamen mihi tenendam esse conspicerem, elegi potius tibi, si quem possem, communicare fructum sermonis, quam tutari me solum portu silentii: simul fiducia habens, si quid forte, quod approbes, dixerim, tuis precibus posse me non superbire; sin autem (quod magis puto) nihil tuo studio dignum effecerim, de nihilo superbire non posse.",
        "And I saw that, though neither of these courses is free from peril, I should be obliged to take one or the other. So I have thought it better to give you the benefit of anything that I can say, than to seek personal safety in the harbour of silence. And I earnestly trust that, if I am fortunate enough to say anything which commends itself to you, I may have in your prayers a safeguard against pride, whereas if — as is more likely — I produce nothing worthy of your attention, there will be no possible cause for conceit.",
        "And when I saw that neither was safe, yet that one or the other must still be held by me, I chose rather to communicate to you, if I could, the fruit of the sermon, than to keep myself alone safe in the harbour of silence: having at the same time the trust that, if I should perhaps have said something you approve, I might by your prayers be able not to grow proud; but if (what I rather think) I should have accomplished nothing worthy of your zeal, I could not grow proud of nothing.",
      ),
    ]),
  ],
};
