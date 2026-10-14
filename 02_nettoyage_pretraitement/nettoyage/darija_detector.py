"""
╔══════════════════════════════════════════════════════════════════════╗
║   DARIJA DETECTOR v3 — Détection robuste Darija marocaine            ║
║   Exclut : MSA, Français, Anglais, Autres langues                    ║
║   Garde  : Darija arabic / latin / mixed uniquement                  ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import re
from dataclasses import dataclass
from typing import Tuple


# ══════════════════════════════════════════════════════════════════════
#  STOPWORDS LANGUES À EXCLURE
# ══════════════════════════════════════════════════════════════════════

FRENCH_STOPWORDS = {
    "le","la","les","un","une","des","du","au","aux",
    "ce","cet","cette","ces","mon","ma","mes","ton","ta","tes",
    "son","sa","ses","notre","votre","leur","leurs",
    "je","tu","il","elle","nous","vous","ils","elles","on",
    "me","te","se","lui","moi","toi","soi",
    "qui","que","quoi","dont","lequel","laquelle",
    "est","sont","suis","es","sommes","êtes",
    "fait","font","faire","dit","dire","vais","vas","va","allons",
    "peut","peuvent","pouvoir","faut","doit","doivent",
    "était","étaient","avait","avaient","sera","seront","serait",
    "avoir","être","aller","venir","voir","savoir","vouloir","devoir",
    "dans","sur","sous","avec","sans","pour","par","vers","chez",
    "entre","pendant","depuis","avant","après","selon","contre","malgré",
    "mais","donc","car","or","ni","si","comme","alors","ainsi",
    "aussi","même","encore","déjà","toujours","jamais","souvent","parfois",
    "très","plus","moins","assez","trop","bien","mal","vite","peu",
    "comment","pourquoi","quand","combien","quel","quelle","quels","quelles",
    "merci","bonjour","bonsoir","bravo","félicitations","chapeau",
    "vraiment","exactement","absolument","effectivement","franchement",
    "continue","continuez","excellent","magnifique","parfait","super",
    "video","vidéo","contenu","chaine","chaîne","abonnez","abonné","like",
}

ENGLISH_STOPWORDS = {
    "the","a","an","is","are","was","were","be","been","being",
    "have","has","do","does","did","will","would","could","should",
    "may","might","shall","must","can",
    "i","you","he","she","we","they","it","me","him","her","us","them",
    "my","your","his","its","our","their",
    "this","that","these","those","what","which","who","whom","whose",
    "where","when","why","how","all","each","every","both","few","more",
    "most","other","some","such","no","not","only","same","so","than",
    "too","very","just","but","and","or","nor","for","yet",
    "in","on","at","to","of","by","with","from","about","as","into",
    "through","during","before","after","above","below","between",
    "if","because","while","although","though","since","unless",
    "think","know","see","look","want","get","make","go","come","say",
    "good","great","like","new","first","last","long","little","own",
    "right","big","high","different","small","large","next","early",
    "okay","yeah","yes","well","really","actually","basically",
    "bro","man","dude","guys","people","thing","things","way","time",
    "year","years","day","days","feel","said","told",
    "answer","question","video","channel","comment","watch","seen",
    "there","here","then","now","still","even","also","back","much",
    "tho","ur","re","ll","dont","doesnt","cant","wont",
    "oh","ohh","okay","ok","im","ive","id",
    "brother","brothers","sister","sisters","friend","friends",
    "waiting","talking","reading","saying","thinking","looking",
    "love","hate","need","hope","wish","let","got","put",
    "research","evidence","prophecy","argument","intention","scholars",
    "guidance","merciful","clarify","confused","capable",
    "pure","clear","guide","guides","reading","quran","islam","muslim",
}

# ══════════════════════════════════════════════════════════════════════
#  BRUIT YOUTUBE / RÉSEAUX SOCIAUX — filtré avant analyse
# ══════════════════════════════════════════════════════════════════════

YOUTUBE_NOISE = {
    # Rires arabes
    "هههه","ههههه","هههههه","هههههههه","هههههههههه",
    # Rires latins
    "lol","lmao","xd","rofl","haha","hahaha","hhh","hhhh",
    # Spam YouTube
    "subscribe","sub","like","likes","comment","share",
    "first","nice","cool","wow","amazing","fire",
    # Emojis texte
    "xD","XD",":-)",":-)",":-D",
}

# Mots Darija latin ambigus avec anglais — ignorés lors de la détection anglais
_DARIJA_EN_AMBIGUOUS = {
    "had","allah","la","al","ya","hi","yo","sir","all","may",
    "a","b","in","no","or","and","on","m","is","be","do","go",
    "inshallah","nshallah","nshala","mashallah","bismillah",
}


# ══════════════════════════════════════════════════════════════════════
#  MOTS ARABES NEUTRES — présents en Darija ET MSA, non discriminants
# ══════════════════════════════════════════════════════════════════════

ARABIC_NEUTRAL = {
    # Pronoms universels
    "انا","هو","هي","هم","نحن","انت","انتم","انتن",
    # Formules religieuses universelles (MSA + Darija + toutes variantes arabes)
    "الله","لله","يرب","ياربي","ربي","والله","بالله","تالله",
    "ماشاء","ماشاءالله","تباركالله","سبحانالله","الحمدلله",
    "إنشالله","نشالله","بسمالله","اللهم",
    "سبحان","الحمد","لله","بسم","الرحمن","الرحيم",
    "صلى","عليه","وسلم","محمد","النبي","رسول",
    "الجنة","النار","القيامة","الآخرة","الاخرة",
    # Salutations universelles
    "السلام","سلام","عليكم","وعليكم","مرحبا","أهلا","أهلاً","مرحباً",
    # Acquiescements
    "نعم","لا","صح","عفوا","عفواً","شكرا","شكراً",
    # Locatifs / déictiques
    "هنا","هناك","هكذا","كذلك","كان",
    # Mots ambigus MSA/Darija
    "كلا","بعيد","بعيدة","قريب","قريبة",
    "كثير","كثيرا","جدا","فقط","أيضا","ايضا",
    # Connecteurs universels
    "في","من","على","إلى","عن","مع","بين","حتى","ثم",
    "لكن","لكنه","لكنها","وان","وإن","فإن",
    # Temporels/conditionnels présents en MSA et Darija
    "لما","ملي","كما","حين","حيث",
}


# ══════════════════════════════════════════════════════════════════════
#  MSA — MARQUEURS INSTITUTIONNELS ET COURANTS
# ══════════════════════════════════════════════════════════════════════

MSA_COMMON = {
    "أنا","أنت","أنتم","أنتن","هو","هي","هم","هن","نحن",
    "هذا","هذه","هذان","هاتان","هؤلاء","ذلك","تلك","أولئك",
    "الذي","التي","الذين","اللواتي","اللتان","اللذان",
    "ماذا","لماذا","كيف","متى","أين","هل",
    "لأن","لأنه","لأنها","لكن","لكنه","لكنها",
    "عندما","حينما","بينما","عندئذ","حينئذ",
    "وإن","وإذا","فإن","فإذا","إذا","كي","لكي",
    "ثم","كذلك","بالإضافة","فضلاً",
    "لذلك","لذا","وبالتالي","ومن ثم","وعليه",
    "ليس","ليست","لن","لم","غير","سوف",
    "جميع","كافة","مختلف","عديد","بعض","خلال","ضمن","نحو",
    "أكثر","أقل","أفضل","أسوأ","أكبر","أصغر",
    "يقول","تقول","يذهب","تذهب","يريد","تريد","أريد",
    "يعمل","تعمل","يعيش","تعيش","يعتقد","تعتقد",
    "يستطيع","تستطيع","استطاع","يحتاج","تحتاج",
}

MSA_MARKERS = {
    "يجب","ينبغي","لابد","يتعين","يستوجب","يلزم",
    "إذ","حيث","بينما","كما","أيضاً","أيضا","كذلك",
    "فضلاً","علاوة","بالإضافة","وبالتالي","لذلك","لذا",
    "وبذلك","نتيجةً","وعليه","تبعاً","وفقاً","طبقاً",
    "نظراً","إذاً","إذن","حينئذ","عندئذ",
    "الحكومة","الحكومي","الحكومية","البرلمان","البرلماني",
    "المؤسسة","المؤسسات","الديمقراطية","الديمقراطي",
    "الصحافة","الصحفي","الإعلام","الإعلامي",
    "المعارضة","الأغلبية","الأقلية","التعددية",
    "الاقتصادي","الاقتصادية","الاقتصاد",
    "الاجتماعي","الاجتماعية",
    "السياسية","السياسي","السياسة",
    "القانونية","القانوني","القانون",
    "الدستورية","الدستوري","الدستور",
    "التشريعية","التشريعي","التشريع",
    "التنفيذية","التنفيذي","القضائية","القضائي",
    "استقالة","الاستقالة","الأحزاب","الحزب",
    "المتظاهرين","المتظاهرون","السلميين","المحتجين",
    "السلطات","المخربين","المواطنين","الشعب","الأمة",
    "المملكة","الجمهورية","الدولة","الحكم","النظام",
    "اللجنة","الهيئة","المجلس","الوزارة","الوزير","الوزراء",
    "المديرية","المحكمة","النيابة",
    "تتضمن","تشمل","يتضمن","يشمل","يتناول","يتطرق","يتعلق",
    "تضمنت","شملت","تناولت","تطرقت",
    "صرح","أكد","أفاد","أشار","أوضح","كشف","أعلن",
    "اقترح","طالب","نادى","دعا","ناشد","حث",
    "إنه","إنها","إنهم","إننا","إنكم","إنك","إنني",
    "التي","الذي","الذين","اللواتي","اللتان","اللذان",
    "المصدر","المصادر","التصريح","البيان","التقرير",
    "الحادثة","الواقعة","الأحداث","المستجدات",
    "الملف","القضية","المسألة","الإشكالية",
    "المسلمون","المؤمنون","الشريعة","الفقه","العلماء","الأئمة",
}


# ══════════════════════════════════════════════════════════════════════
#  LEXIQUE DARIJA LATIN
# ══════════════════════════════════════════════════════════════════════

DARIJA_LATIN = {
    # Pronoms
    "ana","nta","nti","ntina","ntuma","hna","huma","huwa","hiya",
    # Démonstratifs
    "had","hada","hadi","hadak","hadik","hadchi","haduk",
    "dak","dik","duk","lhna","ghda","lyum",
    # Possession
    "dyal","dyali","dyalk","dyalo","dyalha","dyalna","dyalkum","dyalhum",
    "dial","diali","dialk","dialo","dialha","dialna","dialkum","dialhum",
    "tac","ntac","ntab",
    # Prépositions Darija
    "f","mn","l","b","m3a","3la","3nd","3ndi","3ndk","3ndo","3ndha",
    "3ndna","3ndkum","3ndhum","li","lli","liya","lih","liha",
    "bih","biha","bina","bikum","bihum","fih","fiha","fina","fikum",
    "fihum","3lih","3liha","3lina","3likum","3lihum",
    "mnh","mnha","mno","mnna","mnkum","mnhum",
    # Verbes passé
    "bghit","bghiti","bgha","bghat","bghina","bghiw","bghaw",
    "mshit","mshiti","msha","mshat","mshina","mshaw",
    "jit","jiti","ja","jat","jina","jiw","jaw",
    "dert","derti","dar","daret","derna","dertu","daru",
    "klit","kliti","kla","klat","klina","klitu","klaw",
    "shrit","shriti","shra","shrat","shrina","shritu","shraw",
    "glt","glti","gal","galit","glna","gltu","galu",
    "seft","sefti","saf","safet","sefna","seftu","safu",
    "rjt","rjti","rja","rjat","rjna","rjtu","rjaw",
    "wqft","wqfti","wqf","wqfet","wqfna","wqftu","wqfu",
    "fhmt","fhmti","fhm","fhmet","fhmna","fhmtu","fhmu",
    "3rft","3rfti","3rf","3rfet","3rfna","3rftu","3rfu",
    "ktbt","ktbti","ktb","ktbet","ktbna","ktbtu","ktbu",
    "qrit","qriti","qra","qrat","qrina","qritu","qraw",
    "ndir","nro","nmshi","njib","nkul","nshri","nktb",
    "tdir","tro","tmshi","tjib","tkul","tshri","tktb",
    "ydir","yro","ymshi","yjib","ykul","yshri","yktb",
    "kdir","kro","kmshi","kjib","kkul","kshri",
    # Être / état
    "kan","kanet","kanu","knt","kna","kntum",
    "ghadi","ghad","rah","gha","ghir",
    "kayn","kayna","kaynu","mkaynch",
    "zid","zidi","zidu","aji","sir","siri","siru",
    # Négation
    "mashi","machi","makaynch","makainch","makansh",
    "mandir","matdir","maydir","mabghitsh","mamshitsh",
    "makanitsh","mafhmtsh","ma3rftsh",
    # Adverbes
    "bzzaf","bzaf","bzzf","bezaf",
    "chwiya","chwia","shwiya","shwia","chwi",
    "dima","dyma","dema",
    "daba","dba",
    "bkri","bakri","b3id","b3ida","qrib","qriba",
    "hta","ghir","ghi","bass",
    "3ad","3awed","tani","tali",
    "baraka","barka","yak","yakhi",
    "wla","wlla","ola","imma","amma",
    # Interrogatifs
    "wach","wash","wesh","waash",
    "kifash","kfash","kifah","kfah","kif",
    "fin","fayn","feen","fen",
    "chhal","chal","shal",
    "3lash","ash","aash",
    "shkun","shkon","shkn","mnin","mneen",
    # Accord/désaccord
    "wakha","wkha","safi","la","lla","ih","iyh","eeh",
    # Qualificatifs
    "mzyan","mzien","mliha","mli7","zwina","zwin","zwine",
    "7lu","7lwa","7elwa","helwa",
    "kbir","kbira","sghir","sghira","bhal","bhala","b7al",
    "jdid","jdida","qdim","qdima","rkhis","rkhisa","ghali","ghalia",
    "wajib","lazem","lazm","khsso","khssek","khssni",
    # Salutations Darija
    "salam","labas","lbas","bikhir","hamdulah","lhamdulilah",
    "inshallah","nshallah","nshala","bismillah",
    "allah","lah","yak","yrab","yarabi","rabbi",
    "smhli","smhlia","sme7li",
    "hshuma","7shuma","7chouma","hchouma",
    "sahbi","sa7bi","khoya","khouya","khti",
    "lmima","baba","mama","jdda","3mmi","3mmu",
    # Connecteurs
    "walakin","wlkin","wlekin","lkin",
    "hit","7it","7itha","3lhit",
    "ila","mlli",
    # Arabizi
    "m3a","m3ak","m3ah","m3aha","m3akum","m3ahum",
    "3la","3lik","3lih","3liha","3lina","3likum","3lihum",
    "3nd","3ndi","3ndk","3ndna","3ndkum","3ndhum",
    "7it","7itha","7al","7ala","7alla","7awl",
    "b7al","b7alo","b7ala","b7alna","b7alha",
    "9al","9alit","9alha","9alih","9alna",
    "9bel","9bla","9bl","9belha","9belih",
    "t7ssen","y7ssen","n7ssen","7sen",
    "7lib","l7lib","7liba",
    "2mr","l2mr","5bar","l5bar","5abar",
    "5u","5uk","5uh","5una","5ukum","5uhum",
    "7na","7nak","7nah",
    # Quotidien
    "flous","flus","flos","drham","drahim",
    "mdriss","lmdriss","skwila","jami3a",
    "dar","ldar","lbait","lmasjid","lhanout",
    "kla","lkla","lma",
    "nhar","lnhar","lil","llil","sb7","3sha",
    # Numéraux
    "juj","jujhum","tlata","rb3a","khmsa","stta","sb3a","tmnya","ts3ud","3shra",
    "wahd","wa7d","wahda","wa7da",
}


DARIJA_LATIN_EXTRA = {
    # Variantes interrogatifs
    "wach","wash","wesh","waash",
    "ashnu","achno","ashno","shnu","shno",
    # Temporels
    "alyoum","alyom","alyum",
    "lbareh","lbare7",
    # Accord/approbation
    "iwa","iwaa","iwaaa",
    "safi","safii",
    "wakha","wakhaa",
    # État/direction
    "rah","raha","raho","rahom",
    # Famille
    "sahbi","s7abi",
    "khoya","khouya",
    "khti","khtii",
    # Bénédictions Darija latin
    "tbarkallah","tbarkallah3lik","tbarkellah",
    "lahybarek","lahyjazik","lahykhlik",
    "ma3lich","ma3lina",
    # Santé
    "bssa7","bs7","bsa7a",
    # Présent kn- latin
    "kankhdem","kanshof","kansma3","kankol","kanbghit",
    "katkhdem","katshof","katsma3","katkol",
    "kaykhdem","kayshof","kaysma3","kaykol",
    # Variantes supplémentaires
    "ziach","zwich","zwin","zwina",
    "mochkil","mochkila","probleme",
    "chi","chay","shi",
    "haja","hawayej","klshi",
    "nass","lnas","nta3","nta3i",
    "weld","bnet","rajel","mra",
}
DARIJA_LATIN = DARIJA_LATIN | DARIJA_LATIN_EXTRA


# ══════════════════════════════════════════════════════════════════════
#  LEXIQUE DARIJA ARABE
# ══════════════════════════════════════════════════════════════════════

DARIJA_ARABIC = {
    # Interrogatifs dialectaux
    "واش","آش","اشنو","كيفاش","منين","فين","شكون","علاش","شحال",
    # Pronoms dialectaux
    "انا","نتا","نتي","نتوما","حنا","هوما","هو","هي",
    # Démonstratifs dialectaux
    "هادا","هادي","هاداك","هاديك","هادشي","هادوك","دك","ديك",
    "لهنا","هنايا","هداك","هديك",
    # Possession dialectale
    "ديال","ديالي","ديالك","ديالو","ديالها","ديالنا","ديالكم","ديالهم",
    "تاع","تاعي","تاعك","تاعو","تاعها","تاعنا","تاعكم","تاعهم",
    # Verbes passé dialectaux
    "بغيت","بغيتي","بغا","بغات","بغينا","بغيتو","بغاو",
    "مشيت","مشيتي","مشى","مشات","مشينا","مشيتو","مشاو",
    "جيت","جيتي","جا","جات","جينا","جيتو","جاو",
    "درت","درتي","دار","دارت","درنا","درتو","داروا",
    "كليت","كليتي","كلا","كلات","كلينا","كليتو","كلاو",
    "شريت","شريتي","شرى","شرات","شرينا","شريتو","شراو",
    "قلت","قلتي","قالت","قلنا","قلتو","قالوا",
    "فهمت","فهمتي","فهمنا","فهمتو","فهموا",
    "عرفت","عرفتي","عرفنا","عرفتو","عرفوا",
    "كتبت","كتبتي","كتبنا","كتبتو","كتبوا",
    "قريت","قريتي","قرا","قرات","قرينا","قريتو","قراو",
    "شفت","شفتي","شاف","شافت","شفنا","شفتو","شافوا",
    "سمعت","سمعتي","سمعنا","سمعتو","سمعوا",
    "حبيت","حبيتي","حب","حبت","حبينا","حبيتو","حبوا",
    "جاب","جابت","جابو",
    "خرج","خرجت","خرجنا","خرجو",
    "دخل","دخلت","دخلنا","دخلو",
    "وقف","وقفت","وقفنا","وقفو",
    "لبس","لبست","لبسنا","لبسو",
    "طاح","طاحت","طحنا","طاحو",
    "عاد","عادت","عدنا","عادو",
    "رجع","رجعت","رجعنا","رجعو",
    "بقى","بقات","بقينا","بقاو",
    "صار","صارت","صرنا",
    # Présent dialectal (kn-/kt-/ky-)
    "كاين","كاينة","كايني","كاينين",
    "كنمشي","كتمشي","كيمشي","كنمشيو",
    "كنشوف","كتشوف","كيشوف","كنشوفو",
    "كنقول","كتقول","كيقول","كنقولو",
    "كنخدم","كتخدم","كيخدم","كنخدمو",
    "كنبغي","كتبغي","كيبغي","كنبغيو",
    "كنجي","كتجي","كيجي","كنجيو",
    "كندير","كتدير","كيدير","كنديرو",
    "كنسمع","كتسمع","كيسمع","كنسمعو",
    "كنهضر","كتهضر","كيهضر",
    "تعرف","يعرف","نعرف",
    "تشوف","يشوف","نشوف",
    # Négation dialectale (ما...ش)
    "ماشي","مكاينش","ماكاينش","مافيش","ماعندوش","ماعنديش",
    "مابغيتش","مامشيتش","ماجيتش","ماعرفتش","مافهمتش",
    "ماقلتش","ماشفتش","ماسمعتش","ماكانش","مكانش","ماكنتش",
    # Adverbes dialectaux
    "بزاف","شوية","ديما","دابا","بكري",
    "هنايا","فوق","تحت","قدام","ورا",
    "غدا","البارح","دروك","توا",
    # Accord/désaccord
    "واخا","صافي","يه","إيه","لالا","ايه","معلوم",
    "بصح","والو","يمكن",
    # Qualificatifs dialectaux
    "مزيان","مزيانة","مزيانين","مليح","مليحة","مليحين",
    "حلو","حلوة","حلوين","زوين","زوينة","زوينين",
    "خايب","خايبة","خايبين",
    "غالي","غالية","غاليين","رخيص","رخيصة","رخاص",
    # Famille / personnes Darija
    "سمحلي","سمحليا","حشومة","حشوما","عيب",
    "صاحبي","صاحبتي","خويا","خوها","ختي",
    "ماما","بابا","جدة","جد","عمي","عمتي",
    "ولد","وليد","بنت","راجل","مرا","بنادم",
    # Connecteurs dialectaux
    "واكن","ولاكن","حيت","علاش",
    "ملي","مللي","فاش","باش","حاش","كيفما","بحال","لما",
    # Formes verbales manquantes
    "راه","راهو","راها","راهم","راهي","راهنا",
    "بغاش","مابغاش","ماراهش",
    "يجي","تجي","نجي","جاو","جيو",
    "معانا","معاكم","معاهم","معاك","معاه","معاها",
    "كنا","كنتوا","كنتوم","كانوا",
    # Quotidien
    "فلوس","دراهم","درهم","خبز","لخبز","شاي","لشاي",
    "لدار","لقاهوة","لبلاصة","لسوق",
    "لماء","صباح",
    "سبيطار","دكتور","جامعة","مدرسة","دراسة",
    "خدمة","خدمت","باطمة","موظف","تاجر","فلاح",
    "حاجة","حوايج","كلشي","والو",
    # Numéraux dialectaux
    "واحد","جوج","تلاتة","ربعة","خمسة","ستة","سبعة","تمنية","تسعود","عشرة",
    "حداش","طناش","ميا","الف",
    # Expressions YouTube Darija
    "يعطيك","يعطيه","يعطيكم","ربي","بغيت","بغينا",
    "هادشي","هداك","هادي","مزيانة",
}


DARIJA_ARABIC_EXTRA = {
    # Interrogatifs variants
    "اش","اشنو","علاشش",
    "فينك","فينكم","فينهم",
    # Approbation
    "ايوا","ايوه","ايوة","ايه","إيه",
    # Affirmation
    "بصح","بصاح","بصحيح",
    # Accord
    "صافي","واخا","واخا",
    # Bénédictions Darija arabe
    "اللهيحفظك","اللهيبارك","اللهيجازيك",
    "اللهيعطيك","ربيحفظك","ربيبارك",
    # Famille
    "خويا","خوتي","اختي","ختو",
    # Négation contractée
    "ماكنش","ماكاينش","ماشيش","مافيهش",
    "ماقالش","ماجاش","مادارش","ماشافش",
    # Quotidien
    "فلوس","دراهم","كلشي","والوش",
    # Variantes présent
    "كيقرا","كيكتب","كيلعب","كيضحك",
    "كتقرا","كتكتب","كتلعب","كتضحك",
    "كنقرا","كنكتب","كنلعب","كنضحك",
    # Expressions courantes
    "مزيان","بزاف","شوية","دابا","ديما",
    "واعر","واعرة","كيفكيف","فما","لا",
    "راك","راكي","راكم","راهم",
    "خاصك","خاصني","خاصو","خاصها",
}
DARIJA_ARABIC = DARIJA_ARABIC | DARIJA_ARABIC_EXTRA


# ══════════════════════════════════════════════════════════════════════
#  PATTERNS MORPHOLOGIQUES
# ══════════════════════════════════════════════════════════════════════

_SUFFIX_DARIJA  = re.compile(
    r'\b\w+(iti|ina|iwo|shi|shna|shiw|ndi|ndk|ndo|ndha|iya|iyha|iyo|kom|kum|hum)\b',
    re.IGNORECASE
)
_PREFIX_DARIJA  = re.compile(
    r'\b(ma\w+sh\b|ma\w+ch\b|m\w+tsh\b|ndir|tdir|ydir|kdir)\b',
    re.IGNORECASE
)
_ARABIZI        = re.compile(r'\b\w*[2378945]\w*\b')
_ARABIZI_STRONG = re.compile(
    r'\b([3][a-z]+|[a-z]+[3]|[7][a-z]+|[a-z]+[7]|[9][a-z]+|[a-z]+[9]|[a-z]+[2]|[2][a-z]+)\b',
    re.IGNORECASE
)
_CONSONANT      = re.compile(r'\b[bcdfghjklmnpqrstvwxyz]{3,}[aeiou]\b', re.IGNORECASE)

# Morphologie arabe dialectale
_MUDAR_PREFIX   = re.compile(r'[\u0643][\u0646\u062A\u064A][\u0645-\u0646\u062A\u064A\u0641\u062E\u062C\u062D\u0639\u0628\u062F\u0631\u0634\u0633]')
_NEG_MAASH      = re.compile(r'\u0645\u0627[\u0600-\u06FF]+\u0634')   # ما...ش
_PLURAL_WAW     = re.compile(r'[\u0600-\u06FF]{3,}\u0648\b')
_L_ARTICLE      = re.compile(r'\b\u0644[\u062F\u0643\u0646\u0645\u0628\u062E\u062C\u062D\u0639\u0641\u062A\u0631\u0634\u0633]')

# Patterns négatifs Darija supplémentaires
_DARIJA_NEG_LAT = re.compile(r'ma\w+ch', re.IGNORECASE)   # makaynch, mamshitsh...
_DARIJA_NEG_ARA = re.compile(r'ما[؀-ۿ]{2,}ش')  # ما...ش (2+ chars)

# Marqueurs MSA syntaxiques
_MSA_IDAFA      = re.compile(r'\u0627\u0644[\u0600-\u06FF]+\s+\u0627\u0644[\u0600-\u06FF]+')
_MSA_YATAFAAL   = re.compile(r'\u064A[\u062A\u0633][\u0600-\u06FF]{3,}|\u062A[\u062A\u0633][\u0600-\u06FF]{3,}')
_MSA_TANWIN     = re.compile(r'[\u064B\u064C\u064D]')
_MSA_RELATIVE   = re.compile(r'[\u0627\u0644][\u0644\u062B\u0630][\u064A\u0627][\u0646\u0648]?\b')


# ══════════════════════════════════════════════════════════════════════
#  DATACLASS RÉSULTAT
# ══════════════════════════════════════════════════════════════════════

@dataclass
class DarijaScore:
    lexique_lat:  float = 0.0
    lexique_ara:  float = 0.0
    lexique_msa:  float = 0.0
    struct_lat:   float = 0.0
    struct_ara:   float = 0.0
    struct_msa:   float = 0.0
    arabizi:      float = 0.0
    n_words:      int   = 0
    ara_ratio:    float = 0.0
    lat_ratio:    float = 0.0
    is_mixed:     bool  = False
    darija_type:  str   = "other"
    confidence:   float = 0.0

    def darija_sig(self) -> float:
        return (self.lexique_lat * 3.0 + self.lexique_ara * 3.0
                + self.struct_lat * 2.0 + self.struct_ara * 2.0
                + self.arabizi    * 2.5)

    def msa_sig(self) -> float:
        return self.lexique_msa * 3.0 + self.struct_msa * 2.0


# ══════════════════════════════════════════════════════════════════════
#  ANALYSE PRINCIPALE
# ══════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════
#  NORMALISATION TEXTE
# ══════════════════════════════════════════════════════════════════════

def normalize_text(text: str) -> str:
    """Nettoie le texte avant analyse : URLs, mentions, emojis, répétitions."""
    # Supprimer URLs
    text = re.sub(r'https?\S+|www\S+', ' ', text)
    # Supprimer mentions @user
    text = re.sub(r'@\w+', ' ', text)
    # Supprimer emojis unicode (hors alphabet arabe/latin)
    text = re.sub(r'[\U00010000-\U0010ffff]', ' ', text)
    text = re.sub(r'[\u2600-\u27BF]', ' ', text)
    text = re.sub(r'[\uFE00-\uFEFF]', ' ', text)
    # Supprimer rires arabes/latins répétés : ههههه → '', hhhhhh → ''
    text = re.sub(r'[هh]{3,}', ' ', text, flags=re.IGNORECASE)
    # Réduire répétitions excessives de caractères
    text = re.sub(r'(.)\1{3,}', r'\1\1', text)
    # Supprimer caractères parasites (garder arabe, latin, chiffres, espaces)
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    # Supprimer bruit YouTube (mots parasites)
    words = text.split()
    words = [w for w in words if w.lower() not in YOUTUBE_NOISE]
    return " ".join(words).strip()
def analyze(text: str) -> DarijaScore:
    sc = DarijaScore()
    if not text or not isinstance(text, str):
        return sc
    t = normalize_text(text.strip())
    if not t:
        return sc

    # ── Métriques de base ─────────────────────────────────────────
    wlat = re.findall(r'\b[a-zA-Z0-9]{1,25}\b', t.lower())
    wara = re.findall(r'[\u0600-\u06FF]+', t)
    tot  = max(len(wlat) + len(wara), 1)
    nara = sum(1 for c in t if '\u0600' <= c <= '\u06FF')
    nlat = sum(1 for c in t if c.isascii() and c.isalpha())
    ntot = max(len(t), 1)

    sc.n_words   = tot
    sc.ara_ratio = nara / ntot
    sc.lat_ratio = nlat / ntot
    sc.is_mixed  = nara > 2 and nlat > 2

    # ── Couche 1 : lexique ────────────────────────────────────────
    dl = sum(1 for w in wlat if w in DARIJA_LATIN)
    da_all    = [w for w in wara if w in DARIJA_ARABIC]
    da_strong = [w for w in da_all if w not in ARABIC_NEUTRAL]
    da  = len(da_strong) if da_strong else len(da_all) // 2
    msa = sum(1 for w in wara if w in MSA_MARKERS)

    sc.lexique_lat = dl  / tot
    sc.lexique_ara = da  / tot
    sc.lexique_msa = msa / tot

    # ── Détection français ────────────────────────────────────────
    fr_hits  = sum(1 for w in wlat if w in FRENCH_STOPWORDS)
    fr_ratio = fr_hits / max(len(wlat), 1)

    # ── Détection anglais ─────────────────────────────────────────
    # On ignore les mots ambigus (had, allah...) pour ne pas fausser le score
    wlat_clean = [w for w in wlat if w not in _DARIJA_EN_AMBIGUOUS]
    en_hits  = sum(1 for w in wlat_clean if w in ENGLISH_STOPWORDS)
    en_ratio = en_hits / max(len(wlat_clean), 1) if wlat_clean else 0.0
    # Signal Darija fort (hors mots ambigus)
    da_lat_strong = sum(1 for w in wlat_clean if w in DARIJA_LATIN
                        and w not in _DARIJA_EN_AMBIGUOUS)

    # ── Détection MSA commun ──────────────────────────────────────
    msa_com       = sum(1 for w in wara if w in MSA_COMMON)
    msa_com_ratio = msa_com / max(len(wara), 1)

    # ── Couche 2 : structures latines + Arabizi ───────────────────
    slat = (len(_SUFFIX_DARIJA.findall(t))
            + len(_PREFIX_DARIJA.findall(t))
            + len(_CONSONANT.findall(t)))
    sc.struct_lat = min(slat / tot, 1.0)
    az = len(_ARABIZI_STRONG.findall(t))
    sc.arabizi = min(az / tot * 1.5, 1.0)

    # ── Couche 3 : morphologie arabe dialectale ───────────────────
    sara = (len(_MUDAR_PREFIX.findall(t)) * 2
            + len(_NEG_MAASH.findall(t))  * 3
            + len(_PLURAL_WAW.findall(t))
            + len(_L_ARTICLE.findall(t))
            + len(_DARIJA_NEG_ARA.findall(t)) * 2)
    sc.struct_ara = min(sara / tot, 1.0)
    # Boost struct_lat via patterns négatifs latins
    sc.struct_lat = min(sc.struct_lat + len(_DARIJA_NEG_LAT.findall(t)) / tot, 1.0)

    # ── Couche 4 : marqueurs MSA syntaxiques ──────────────────────
    smsa = (len(_MSA_IDAFA.findall(t))     * 2
            + len(_MSA_YATAFAAL.findall(t))
            + len(_MSA_TANWIN.findall(t))  * 3
            + len(_MSA_RELATIVE.findall(t)))
    sc.struct_msa = min(smsa / tot, 1.0)

    ds = sc.darija_sig()
    ms = sc.msa_sig()

    # ══════════════════════════════════════════════════════════════
    #  RÈGLES DE DÉCISION — du plus strict au plus permissif
    # ══════════════════════════════════════════════════════════════

    # ── R1. FRANÇAIS PUR ──────────────────────────────────────────
    if fr_ratio > 0.30 and sc.arabizi < 0.10 and sc.lexique_lat < 0.10:
        sc.darija_type = "french"
        sc.confidence  = fr_ratio
        return sc

    # ── R2. FRANÇAIS DOMINANT ─────────────────────────────────────
    if fr_ratio > 0.20 and fr_ratio > (sc.lexique_lat + sc.arabizi) * 2:
        sc.darija_type = "french"
        sc.confidence  = fr_ratio
        return sc

    # ── R2b. Mots universels seuls + signal FR ────────────────────
    _UNIVERSAL = {"inshallah","nshallah","nshala","mashallah","maashallah",
                  "alhamdulillah","hamdulah","bismillah","allah","inch","incha"}
    darija_only = [w for w in wlat if w in DARIJA_LATIN and w not in _UNIVERSAL]
    if (sc.lexique_lat > 0 and len(darija_only) == 0
            and sc.arabizi < 0.10 and sc.struct_lat < 0.05
            and fr_ratio > 0.15):
        sc.darija_type = "french"
        sc.confidence  = fr_ratio
        return sc

    # ── R3. ANGLAIS ───────────────────────────────────────────────
    # Texte latin avec fort ratio anglais ET aucun signal Darija fort
    if (sc.lat_ratio > 0.25                # texte majoritairement latin
            and en_ratio > 0.30            # >30% de mots anglais identifiés
            and da_lat_strong == 0         # aucun mot Darija fort non-ambigu
            and sc.arabizi == 0.0          # aucun Arabizi (3, 7, 9...)
            and fr_ratio < 0.20):          # pas de français non plus
        sc.darija_type = "other"
        sc.confidence  = en_ratio
        return sc

    # ── R4. MSA INSTITUTIONNEL ────────────────────────────────────
    if ms > 1.2 and ms > ds * 1.5:
        sc.darija_type = "msa"
        sc.confidence  = min(ms / (ms + ds + 0.1), 1.0)
        return sc

    # ── R5. MSA COMMUN ────────────────────────────────────────────
    if msa_com_ratio > 0.30 and sc.lexique_ara < 0.10 and sc.struct_ara < 0.15:
        sc.darija_type = "msa"
        sc.confidence  = msa_com_ratio
        return sc

    # ── R6. ARABE SANS MARQUEUR DARIJA ───────────────────────────
    if (sc.ara_ratio > 0.5 and sc.lexique_ara < 0.05
            and sc.struct_ara < 0.10 and msa_com_ratio > 0.15 and tot >= 3):
        sc.darija_type = "msa"
        sc.confidence  = msa_com_ratio
        return sc

    # ── R7. RÈGLE STRICTE DENSITÉ DARIJA ─────────────────────────
    #
    #   Principe : on ne garde que les textes où le Darija est clairement
    #   présent. On calcule la densité de mots Darija forts (hors neutres).
    #
    #   Cas A — density == 0 ET pas de structure dialectale (ما...ش etc.)
    #            → MSA/Religieux certain, quelle que soit la longueur
    #   Cas B — density < 0.08 ET texte > 10 mots
    #            → MSA formel (hadith, fiqh, discours...)
    #
    if sc.ara_ratio > 0.5:
        da_strong_count = sum(
            1 for w in wara
            if w in DARIJA_ARABIC and w not in ARABIC_NEUTRAL
        )
        darija_density = da_strong_count / max(len(wara), 1)

        # Cas A : aucun mot Darija fort ET structure dialectale faible
        #   (seuil 0.30 pour absorber les faux positifs des patterns sur textes courts)
        if darija_density == 0.0 and sc.struct_ara < 0.30:
            sc.darija_type = "msa"
            sc.confidence  = 1.0
            return sc

        # Cas B : très peu de Darija sur un texte long
        if darija_density < 0.08 and tot > 10:
            sc.darija_type = "msa"
            sc.confidence  = round(1.0 - darija_density, 4)
            return sc

    # ══════════════════════════════════════════════════════════════
    #  DÉCISIONS POSITIVES DARIJA
    # ══════════════════════════════════════════════════════════════

    lat_d = sc.lexique_lat + sc.struct_lat + sc.arabizi
    ara_d = sc.lexique_ara + sc.struct_ara

    # Mixte : latin + arabe tous deux présents
    if (lat_d > 0.10 and sc.lat_ratio > 0.3
            and sc.lat_ratio < 0.75 and sc.ara_ratio > 0.15):
        sc.darija_type = "darija_mixed"
        sc.confidence  = min(lat_d + sc.lexique_ara, 1.0)
        return sc

    # Latin pur
    if lat_d > 0.15 and sc.lat_ratio > 0.4:
        sc.darija_type = "darija_latin"
        sc.confidence  = min(lat_d, 1.0)
        return sc

    # Arabizi dominant
    if sc.arabizi > 0.20 and sc.lat_ratio > 0.3:
        sc.darija_type = "darija_latin"
        sc.confidence  = sc.arabizi
        return sc

    # Arabe dialectal
    if ara_d > 0.12 and sc.ara_ratio > 0.35:
        sc.darija_type = "darija_arabic"
        sc.confidence  = min(ara_d, 1.0)
        return sc

    # ══════════════════════════════════════════════════════════════
    #  FALLBACKS (avec garde-fous)
    # ══════════════════════════════════════════════════════════════

    # Arabe sans MSA → Darija SEULEMENT si au moins 1 mot Darija fort
    if (sc.ara_ratio > 0.6 and ms < 0.5
            and msa_com_ratio < 0.25 and tot >= 3
            and len(da_strong) >= 1):
        sc.darija_type = "darija_arabic"
        sc.confidence  = 0.55
        return sc

    # Latin sans FR ni AN → Darija SEULEMENT si pas d'anglais
    if (sc.lat_ratio > 0.6 and ms < 0.1
            and fr_ratio < 0.20 and en_ratio < 0.30 and tot >= 4):
        sc.darija_type = "darija_latin"
        sc.confidence  = 0.55
        return sc

    # Mixte avec signal Darija minimal
    if sc.is_mixed and (lat_d + ara_d) > 0.05:
        sc.darija_type = "darija_mixed"
        sc.confidence  = min(lat_d + ara_d, 1.0)
        return sc

    if sc.is_mixed and ms < 0.3 and fr_ratio < 0.15 and en_ratio < 0.25:
        sc.darija_type = "darija_mixed"
        sc.confidence  = 0.45
        return sc

    sc.darija_type = "other"
    sc.confidence  = 0.0
    return sc


# ══════════════════════════════════════════════════════════════════════
#  API PUBLIQUE
# ══════════════════════════════════════════════════════════════════════

def classify(text: str) -> Tuple[str, float]:
    """Retourne (darija_type, confidence)."""
    r = analyze(text)
    return r.darija_type, r.confidence


def should_keep(text: str, min_words: int = 2, min_conf: float = 0.15) -> bool:
    """True si le texte est du Darija avec qualité suffisante.
    
    Args:
        text      : texte à évaluer
        min_words : nombre minimum de mots (défaut 2, exclut 👍 / هههه)
        min_conf  : confiance minimum (défaut 0.15)
    """
    if not text or len(text.split()) < min_words:
        return False
    dtype, conf = classify(text)
    if conf < min_conf:
        return False
    return dtype in ("darija_latin", "darija_arabic", "darija_mixed")


# ══════════════════════════════════════════════════════════════════════
#  TESTS INTÉGRÉS
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        # ── Darija à GARDER ──────────────────────────────────────
        ("سلام دكتوره انا وجهي فيه حبوب بزاف رقيق وغليظ",    "darija_arabic", "Darija médical"),
        ("هادي خاسها فيديو آخر للناس اللي مكيقراوش",          "darija_arabic", "Darija arabe"),
        ("Mskine ta7 mn sta7",                                  "darija_latin",  "Arabizi"),
        ("Hadi 7El9a zwina bzzaf",                              "darija_latin",  "Arabizi fort"),
        ("bzzaf mzyan had lfilm khdmna fiha",                   "darija_latin",  "Darija latin pur"),
        ("m3a sahbi mshina l7anout w shrina chi 7wija",         "darija_latin",  "Arabizi m3a"),
        ("كنمشي للمدرسة كل نهار مع خويا",                     "darija_arabic", "Préfixe kn-"),
        ("ماعندوش لفلوس ديالو كاع ماشي مزيان",                "darija_arabic", "Négation ماش"),
        ("واش كاين chi doctor zwina ف casablanca بزاف",        "darija_mixed",  "Mélange ar+lat"),
        ("3la khatirak khoya walakin mabghitsh",                "darija_latin",  "Arabizi + négation"),
        ("fin ghadi nta lyum f had lnhar",                      "darija_latin",  "Darija latin hors lex"),
        ("راه ما بغاش يجي معانا فاش كنا كاملين هناك",         "darija_arabic", "Darija narratif"),
        ("واش الشيخ اصبح يترك فسحة للاسئلة",                  "darija_arabic", "Darija question"),
        ("بغيت نسولك على حفظ القران واش ضروري",               "darija_arabic", "Darija + Coran"),
        ("فين كاين هاد الجامع",                                "darija_arabic", "Darija court"),
        ("ماتحشمش تهدر على الشيخ هكذا",                       "darija_arabic", "Darija négation2"),
        ("باش يجاوبك الشيخ خاصك رقمو الخاص ماشي هنا",        "darija_arabic", "Darija instruction"),
        ("واش المجالس ديال الموطا لي كيدير الشيخ فالرباط",   "darija_arabic", "Darija informatif"),
        ("بالله عليكم اليهود حاكمين العالم حنا مزال فباب الصيام", "darija_arabic", "Darija commentaire"),
        ("ربي يعطيك الصحة والله مزيان بزاف",                  "darija_arabic", "Darija religieux"),
        ("بغينا عفاكم محاضرة سيدي افني",                      "darija_arabic", "Darija demande"),
        ("خويا ضروري ختمة القران ياك",                        "darija_arabic", "Darija court2"),
        ("Tbarkellah 3lik",                                     "darija_latin",  "Darija latin court"),
        ("MACHALAH Sa3d akemali ohibouk a fi alah y akhi",     "darija_latin",  "Darija latin mélangé"),

        # ── MSA à EXCLURE ────────────────────────────────────────
        ("يجب استقالة جميع الأحزاب السياسية في المغرب",        "msa", "MSA institutionnel"),
        ("وأشار المسؤول أن الحكومة اتخذت قرارات هامة وفقاً",   "msa", "MSA journalistique"),
        ("يتعين على البرلمان التشريعي إصدار القوانين اللازمة",  "msa", "MSA législatif"),
        ("هذا الكتاب الذي قرأته كان جميلاً جداً وأنصح بقراءته","msa", "MSA commun"),
        ("قال رسول الله اكثرو من قراءة القران الكريم فانه ياتي يوم القيامة شفيعا لاصحابه", "msa", "Hadith"),
        ("لقد بان حالك يا مبتدع جملة من اثار السلف في التحذير من مجالسة اهل البدع وسماعهم", "msa", "Citation salaf"),
        ("تتابع صوم كفارة اليمين الحنابلة والحنفية يلزمان التتابع المالكية يجوز ترك التتابع", "msa", "Fiqh"),
        ("السلام عليكم وعلي المسلمين في العالمين والحمد لله الذي امد بالعمر ويا فلذات اكبادي", "msa", "Discours religieux"),
        ("اللهم صل علي سيدنا محمد الفاتح لما اغلق والخاتم لما سبق ناصر الحق بالحق والهادي", "msa", "Salawat"),
        ("سبحان الله والحمد لله والله اكبر",                   "msa", "Dhikr court"),
        ("جزاكم الله خيرا وبارك الله فيكم",                   "msa", "Dua court"),
        ("بارك الله فيك وجزاك الله خيرا يا شيخنا",            "msa", "Dua court2"),
        ("اللهم بارك وزد لنا علما نافعا",                     "msa", "Dua court3"),
        ("صلوا على رسول الله عليه الصلاة والسلام",             "msa", "Salawat court"),
        ("لا اله الا الله محمد رسول الله",                    "msa", "Shahada"),
        ("الله اكبر كبيرا سبحان الله والحمدلله",              "msa", "Dhikr court2"),
        ("نصركم الله ايدكم الله",                              "msa", "Dua 4w"),
        ("حفظكم المولى ان شاء الله نصر من الله",              "msa", "Dua 8w"),
        ("اللهم انا نسالك انك انت العزيز الحكيم",             "msa", "Dua formel"),
        ("لا تغلو يا اخي حتي الشيخ لا يزعم لنفسه ما ذكرت",  "msa", "MSA court 11w"),
        ("الامر بسيط من اليوتيوب اكتب دروس الموطا وسوف تظهر لك وستستفيد", "msa", "MSA informatif"),

        # ── FRANÇAIS à EXCLURE ───────────────────────────────────
        ("c'est vraiment une très bonne vidéo merci pour le contenu", "french", "Français pur"),
        ("je suis complètement d'accord avec toi continue comme ça",  "french", "Français pur 2"),
        ("bravo pour cette vidéo magnifique tu es le meilleur",       "french", "Français YouTube"),
        ("bonjour est ce que vous pouvez faire une vidéo sur ce sujet","french", "Français question"),
        ("félicitations pour votre travail c'est exactement ce qu'il fallait", "french", "Français félicitations"),

        # ── ANGLAIS à EXCLURE ────────────────────────────────────
        ("We love you ziach",                                   "other", "Anglais court"),
        ("Still waiting for the answer",                        "other", "Anglais court2"),
        ("still no clear answer",                               "other", "Anglais court3"),
        ("Do your own research bro Years ago i had a lot of questions and when i asked my friends i thought there's no answers because of their ignorance", "other", "Anglais long"),
        ("i think he has to specify why is that evidence proves the profecy of a rassol like for example he talks about Roum", "other", "Anglais long2"),
        ("Ohh okay I thought you were confused You're talking about the way he treated the argument He has a good intention tho", "other", "Anglais long3"),
        ("May Allah guide all of us",                           "other", "Anglais religieux"),
        ("There's more scholars capable to clarify the idea",   "other", "Anglais académique"),
        ("Read the Quran with a pure intention you will see the guidance of the most merciful", "other", "Anglais YouTube"),
    ]

    print("=" * 70)
    print("  DARIJA DETECTOR v3 — Suite complète de tests")
    print("=" * 70)
    ok_count = 0
    sections = {
        "Darija": [], "MSA": [], "Français": [], "Anglais": []
    }
    results = []
    for txt, expected, desc in tests:
        dt, conf = classify(txt)
        ok = dt == expected or (expected in ("msa","other") and dt in ("msa","other"))
        results.append((ok, dt, conf, expected, desc))
        if ok:
            ok_count += 1

    for ok, dt, conf, expected, desc in results:
        icon = "✓" if ok else "✗"
        note = f"  ← attendu: {expected}" if not ok else ""
        print(f"  {icon} [{dt:<15}] {conf:.2f}  {desc}{note}")

    print(f"\n  {ok_count}/{len(tests)} ✓  ({ok_count/len(tests)*100:.0f}%)")