const USDT_ABI = ["function transfer(address to, uint256 value) returns (bool)"];

const DEFAULT_CONFIG = {
  apiBaseUrl: "/api/v1",
  chainId: 1,
  chainName: "Ethereum Mainnet",
  tokenSymbol: "USDT",
  tokenStandard: "ERC-20",
  tokenAddress: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
  treasuryAddress: "0xC5AbC4ffE1d53d480dcadcdc4d2ccb66Fe96C47a",
  contractAddress: "backend-verified-rounds",
  lotteryName: "MacBook Neo Drop",
  prizeName: "Новый MacBook Neo",
  totalTickets: 100,
  ticketPrice: 10,
  ticketPriceMicro: 10_000_000,
  maxTicketsPerPurchase: 20,
  walletRequired: true,
  shippingStartDate: "2026-03-11",
};

const storageKeys = {
  theme: "winspot24.theme.v2",
  language: "winspot24.language.v1",
};

const LANGUAGE_OPTIONS = [
  { code: "en", label: "English" },
  { code: "ru", label: "Русский" },
  { code: "es", label: "Español" },
  { code: "fr", label: "Français" },
  { code: "de", label: "Deutsch" },
  { code: "it", label: "Italiano" },
  { code: "pt", label: "Português" },
  { code: "tr", label: "Türkçe" },
  { code: "ar", label: "العربية" },
  { code: "hi", label: "हिन्दी" },
  { code: "zh", label: "中文" },
  { code: "ja", label: "日本語" },
  { code: "ko", label: "한국어" },
  { code: "id", label: "Bahasa Indonesia" },
  { code: "vi", label: "Tiếng Việt" },
  { code: "th", label: "ไทย" },
  { code: "pl", label: "Polski" },
  { code: "nl", label: "Nederlands" },
  { code: "uk", label: "Українська" },
  { code: "fa", label: "فارسی" },
  { code: "he", label: "עברית" },
  { code: "ms", label: "Bahasa Melayu" },
  { code: "bn", label: "বাংলা" },
  { code: "ur", label: "اردو" },
  { code: "ta", label: "தமிழ்" },
];

const UI_TRANSLATIONS = {
  en: {
    nav_round: "Round",
    nav_how: "How it works",
    nav_trust: "Transparency",
    status_open: "Round open",
    status_closed: "Round closed",
    status_need_wallet: "Wallet required",
    purchase_title: "Ticket purchase",
    buy_button: "Buy tickets",
    draw_button: "Finalize draw",
    history_title: "Round history",
    delivery_title: "Public shipping from Dubai",
    shipping_title: "Shipping address (for winner)",
    connect_wallet: "Connect Wallet",
    wallet_connected: "Wallet Connected",
    wallet_disconnected: "Disconnected",
    theme_dark: "Dark Mode",
    theme_light: "Light Mode",
  },
  ru: {
    nav_round: "Раунд",
    nav_how: "Как это работает",
    nav_trust: "Прозрачность",
    status_open: "Раунд открыт",
    status_closed: "Раунд закрыт",
    status_need_wallet: "Нужен кошелек",
    purchase_title: "Покупка билетов",
    buy_button: "Купить билеты",
    draw_button: "Завершить розыгрыш",
    history_title: "История раундов",
    delivery_title: "Публичная доставка из Дубая",
    shipping_title: "Адрес доставки (для победителя)",
    connect_wallet: "Подключить кошелек",
    wallet_connected: "Кошелек подключен",
    wallet_disconnected: "Отключен",
    theme_dark: "Темная тема",
    theme_light: "Светлая тема",
  },
  es: {
    nav_round: "Ronda",
    nav_how: "Cómo funciona",
    nav_trust: "Transparencia",
    status_open: "Ronda abierta",
    status_closed: "Ronda cerrada",
    status_need_wallet: "Cartera requerida",
    purchase_title: "Compra de boletos",
    buy_button: "Comprar boletos",
    draw_button: "Finalizar sorteo",
    history_title: "Historial de rondas",
    delivery_title: "Envío público desde Dubái",
    shipping_title: "Dirección de envío (ganador)",
    connect_wallet: "Conectar cartera",
    wallet_connected: "Cartera conectada",
    wallet_disconnected: "Desconectada",
    theme_dark: "Modo oscuro",
    theme_light: "Modo claro",
  },
  fr: {
    nav_round: "Tour",
    nav_how: "Fonctionnement",
    nav_trust: "Transparence",
    status_open: "Tour ouvert",
    status_closed: "Tour fermé",
    status_need_wallet: "Wallet requis",
    purchase_title: "Achat de billets",
    buy_button: "Acheter des billets",
    draw_button: "Finaliser le tirage",
    history_title: "Historique des tours",
    delivery_title: "Livraison publique depuis Dubaï",
    shipping_title: "Adresse de livraison (gagnant)",
    connect_wallet: "Connecter le wallet",
    wallet_connected: "Wallet connecté",
    wallet_disconnected: "Déconnecté",
    theme_dark: "Mode sombre",
    theme_light: "Mode clair",
  },
  de: {
    nav_round: "Runde",
    nav_how: "So funktioniert es",
    nav_trust: "Transparenz",
    status_open: "Runde offen",
    status_closed: "Runde geschlossen",
    status_need_wallet: "Wallet erforderlich",
    purchase_title: "Ticketkauf",
    buy_button: "Tickets kaufen",
    draw_button: "Auslosung abschließen",
    history_title: "Rundenverlauf",
    delivery_title: "Öffentliche Lieferung aus Dubai",
    shipping_title: "Lieferadresse (Gewinner)",
    connect_wallet: "Wallet verbinden",
    wallet_connected: "Wallet verbunden",
    wallet_disconnected: "Getrennt",
    theme_dark: "Dunkler Modus",
    theme_light: "Heller Modus",
  },
  it: {
    nav_round: "Round",
    nav_how: "Come funziona",
    nav_trust: "Trasparenza",
    status_open: "Round aperto",
    status_closed: "Round chiuso",
    status_need_wallet: "Wallet richiesto",
    purchase_title: "Acquisto biglietti",
    buy_button: "Acquista biglietti",
    draw_button: "Finalizza estrazione",
    history_title: "Storico round",
    delivery_title: "Spedizione pubblica da Dubai",
    shipping_title: "Indirizzo di spedizione (vincitore)",
    connect_wallet: "Connetti wallet",
    wallet_connected: "Wallet connesso",
    wallet_disconnected: "Disconnesso",
    theme_dark: "Modalita scura",
    theme_light: "Modalita chiara",
  },
  pt: {
    nav_round: "Rodada",
    nav_how: "Como funciona",
    nav_trust: "Transparencia",
    status_open: "Rodada aberta",
    status_closed: "Rodada encerrada",
    status_need_wallet: "Carteira obrigatoria",
    purchase_title: "Compra de bilhetes",
    buy_button: "Comprar bilhetes",
    draw_button: "Finalizar sorteio",
    history_title: "Historico de rodadas",
    delivery_title: "Envio publico de Dubai",
    shipping_title: "Endereco de envio (vencedor)",
    connect_wallet: "Conectar carteira",
    wallet_connected: "Carteira conectada",
    wallet_disconnected: "Desconectada",
    theme_dark: "Modo escuro",
    theme_light: "Modo claro",
  },
  tr: {
    nav_round: "Tur",
    nav_how: "Nasil calisir",
    nav_trust: "Seffaflik",
    status_open: "Tur acik",
    status_closed: "Tur kapali",
    status_need_wallet: "Cuzdan gerekli",
    purchase_title: "Bilet satin alma",
    buy_button: "Bilet al",
    draw_button: "Cekilisi sonlandir",
    history_title: "Tur gecmisi",
    delivery_title: "Dubai'den acik kargo takibi",
    shipping_title: "Teslimat adresi (kazanan)",
    connect_wallet: "Cuzdan bagla",
    wallet_connected: "Cuzdan baglandi",
    wallet_disconnected: "Bagli degil",
    theme_dark: "Koyu tema",
    theme_light: "Acik tema",
  },
  ar: {
    nav_round: "الجولة",
    nav_how: "كيف يعمل",
    nav_trust: "الشفافية",
    status_open: "الجولة مفتوحة",
    status_closed: "الجولة مغلقة",
    status_need_wallet: "المحفظة مطلوبة",
    purchase_title: "شراء التذاكر",
    buy_button: "شراء التذاكر",
    draw_button: "إنهاء السحب",
    history_title: "سجل الجولات",
    delivery_title: "تتبع الشحن العام من دبي",
    shipping_title: "عنوان الشحن (للفائز)",
    connect_wallet: "ربط المحفظة",
    wallet_connected: "المحفظة متصلة",
    wallet_disconnected: "غير متصل",
    theme_dark: "الوضع الداكن",
    theme_light: "الوضع الفاتح",
  },
  hi: {
    nav_round: "राउंड",
    nav_how: "यह कैसे काम करता है",
    nav_trust: "पारदर्शिता",
    status_open: "राउंड खुला है",
    status_closed: "राउंड बंद है",
    status_need_wallet: "वॉलेट आवश्यक है",
    purchase_title: "टिकट खरीद",
    buy_button: "टिकट खरीदें",
    draw_button: "ड्रॉ पूरा करें",
    history_title: "राउंड इतिहास",
    delivery_title: "दुबई से सार्वजनिक डिलीवरी ट्रैक",
    shipping_title: "डिलीवरी पता (विजेता)",
    connect_wallet: "वॉलेट कनेक्ट करें",
    wallet_connected: "वॉलेट कनेक्टेड",
    wallet_disconnected: "डिस्कनेक्टेड",
    theme_dark: "डार्क मोड",
    theme_light: "लाइट मोड",
  },
  zh: {
    nav_round: "轮次",
    nav_how: "运作方式",
    nav_trust: "透明度",
    status_open: "轮次进行中",
    status_closed: "轮次已关闭",
    status_need_wallet: "需要钱包",
    purchase_title: "购票",
    buy_button: "购买票券",
    draw_button: "完成开奖",
    history_title: "轮次历史",
    delivery_title: "迪拜公开物流进度",
    shipping_title: "收货地址（中奖者）",
    connect_wallet: "连接钱包",
    wallet_connected: "钱包已连接",
    wallet_disconnected: "未连接",
    theme_dark: "深色模式",
    theme_light: "浅色模式",
  },
  ja: {
    nav_round: "ラウンド",
    nav_how: "仕組み",
    nav_trust: "透明性",
    status_open: "ラウンド開催中",
    status_closed: "ラウンド終了",
    status_need_wallet: "ウォレットが必要",
    purchase_title: "チケット購入",
    buy_button: "チケットを購入",
    draw_button: "抽選を確定",
    history_title: "ラウンド履歴",
    delivery_title: "ドバイからの配送ステータス",
    shipping_title: "配送先住所（当選者）",
    connect_wallet: "ウォレット接続",
    wallet_connected: "接続済み",
    wallet_disconnected: "未接続",
    theme_dark: "ダークモード",
    theme_light: "ライトモード",
  },
  ko: {
    nav_round: "라운드",
    nav_how: "작동 방식",
    nav_trust: "투명성",
    status_open: "라운드 진행중",
    status_closed: "라운드 종료",
    status_need_wallet: "지갑 필요",
    purchase_title: "티켓 구매",
    buy_button: "티켓 구매",
    draw_button: "추첨 확정",
    history_title: "라운드 기록",
    delivery_title: "두바이 배송 공개 추적",
    shipping_title: "배송 주소(당첨자)",
    connect_wallet: "지갑 연결",
    wallet_connected: "지갑 연결됨",
    wallet_disconnected: "연결 안됨",
    theme_dark: "다크 모드",
    theme_light: "라이트 모드",
  },
  id: {
    nav_round: "Ronde",
    nav_how: "Cara kerja",
    nav_trust: "Transparansi",
    status_open: "Ronde dibuka",
    status_closed: "Ronde ditutup",
    status_need_wallet: "Dompet diperlukan",
    purchase_title: "Pembelian tiket",
    buy_button: "Beli tiket",
    draw_button: "Selesaikan undian",
    history_title: "Riwayat ronde",
    delivery_title: "Pelacakan publik dari Dubai",
    shipping_title: "Alamat pengiriman (pemenang)",
    connect_wallet: "Hubungkan dompet",
    wallet_connected: "Dompet terhubung",
    wallet_disconnected: "Terputus",
    theme_dark: "Mode gelap",
    theme_light: "Mode terang",
  },
  vi: {
    nav_round: "Vong",
    nav_how: "Cach hoat dong",
    nav_trust: "Minh bach",
    status_open: "Vong dang mo",
    status_closed: "Vong da dong",
    status_need_wallet: "Can vi",
    purchase_title: "Mua ve",
    buy_button: "Mua ve",
    draw_button: "Chot ket qua",
    history_title: "Lich su vong",
    delivery_title: "Theo doi giao hang cong khai tu Dubai",
    shipping_title: "Dia chi giao hang (nguoi thang)",
    connect_wallet: "Ket noi vi",
    wallet_connected: "Da ket noi vi",
    wallet_disconnected: "Chua ket noi",
    theme_dark: "Che do toi",
    theme_light: "Che do sang",
  },
  th: {
    nav_round: "รอบ",
    nav_how: "วิธีการทำงาน",
    nav_trust: "ความโปร่งใส",
    status_open: "รอบเปิดอยู่",
    status_closed: "รอบปิดแล้ว",
    status_need_wallet: "ต้องใช้วอลเล็ต",
    purchase_title: "ซื้อตั๋ว",
    buy_button: "ซื้อตั๋ว",
    draw_button: "สรุปผลจับรางวัล",
    history_title: "ประวัติรอบ",
    delivery_title: "ติดตามการจัดส่งจากดูไบแบบสาธารณะ",
    shipping_title: "ที่อยู่จัดส่ง (ผู้ชนะ)",
    connect_wallet: "เชื่อมต่อวอลเล็ต",
    wallet_connected: "เชื่อมต่อแล้ว",
    wallet_disconnected: "ไม่ได้เชื่อมต่อ",
    theme_dark: "โหมดมืด",
    theme_light: "โหมดสว่าง",
  },
  pl: {
    nav_round: "Runda",
    nav_how: "Jak to dziala",
    nav_trust: "Przejrzystosc",
    status_open: "Runda otwarta",
    status_closed: "Runda zamknieta",
    status_need_wallet: "Wymagany portfel",
    purchase_title: "Zakup biletow",
    buy_button: "Kup bilety",
    draw_button: "Zakoncz losowanie",
    history_title: "Historia rund",
    delivery_title: "Publiczna dostawa z Dubaju",
    shipping_title: "Adres dostawy (zwyciezca)",
    connect_wallet: "Polacz portfel",
    wallet_connected: "Portfel polaczony",
    wallet_disconnected: "Rozlaczony",
    theme_dark: "Tryb ciemny",
    theme_light: "Tryb jasny",
  },
  nl: {
    nav_round: "Ronde",
    nav_how: "Hoe het werkt",
    nav_trust: "Transparantie",
    status_open: "Ronde open",
    status_closed: "Ronde gesloten",
    status_need_wallet: "Wallet vereist",
    purchase_title: "Tickets kopen",
    buy_button: "Tickets kopen",
    draw_button: "Trekking afronden",
    history_title: "Rondegeschiedenis",
    delivery_title: "Openbare levering vanuit Dubai",
    shipping_title: "Verzendadres (winnaar)",
    connect_wallet: "Wallet verbinden",
    wallet_connected: "Wallet verbonden",
    wallet_disconnected: "Niet verbonden",
    theme_dark: "Donkere modus",
    theme_light: "Lichte modus",
  },
  uk: {
    nav_round: "Раунд",
    nav_how: "Як це працює",
    nav_trust: "Прозорість",
    status_open: "Раунд відкрито",
    status_closed: "Раунд закрито",
    status_need_wallet: "Потрібен гаманець",
    purchase_title: "Купівля квитків",
    buy_button: "Купити квитки",
    draw_button: "Завершити розіграш",
    history_title: "Історія раундів",
    delivery_title: "Публічна доставка з Дубая",
    shipping_title: "Адреса доставки (переможець)",
    connect_wallet: "Підключити гаманець",
    wallet_connected: "Гаманець підключено",
    wallet_disconnected: "Відключено",
    theme_dark: "Темна тема",
    theme_light: "Світла тема",
  },
  fa: {
    nav_round: "دور",
    nav_how: "نحوه کار",
    nav_trust: "شفافیت",
    status_open: "دور باز است",
    status_closed: "دور بسته است",
    status_need_wallet: "کیف پول لازم است",
    purchase_title: "خرید بلیت",
    buy_button: "خرید بلیت",
    draw_button: "نهایی سازی قرعه کشی",
    history_title: "تاریخچه دورها",
    delivery_title: "رهگیری عمومی ارسال از دبی",
    shipping_title: "آدرس ارسال (برنده)",
    connect_wallet: "اتصال کیف پول",
    wallet_connected: "کیف پول متصل",
    wallet_disconnected: "قطع شده",
    theme_dark: "حالت تیره",
    theme_light: "حالت روشن",
  },
  he: {
    nav_round: "סבב",
    nav_how: "איך זה עובד",
    nav_trust: "שקיפות",
    status_open: "הסבב פתוח",
    status_closed: "הסבב סגור",
    status_need_wallet: "נדרש ארנק",
    purchase_title: "רכישת כרטיסים",
    buy_button: "קנה כרטיסים",
    draw_button: "סיים הגרלה",
    history_title: "היסטוריית סבבים",
    delivery_title: "מעקב משלוח ציבורי מדובאי",
    shipping_title: "כתובת משלוח (זוכה)",
    connect_wallet: "חבר ארנק",
    wallet_connected: "ארנק מחובר",
    wallet_disconnected: "מנותק",
    theme_dark: "מצב כהה",
    theme_light: "מצב בהיר",
  },
  ms: {
    nav_round: "Pusingan",
    nav_how: "Cara ia berfungsi",
    nav_trust: "Ketelusan",
    status_open: "Pusingan dibuka",
    status_closed: "Pusingan ditutup",
    status_need_wallet: "Dompet diperlukan",
    purchase_title: "Pembelian tiket",
    buy_button: "Beli tiket",
    draw_button: "Selesaikan cabutan",
    history_title: "Sejarah pusingan",
    delivery_title: "Penjejakan penghantaran awam dari Dubai",
    shipping_title: "Alamat penghantaran (pemenang)",
    connect_wallet: "Sambung dompet",
    wallet_connected: "Dompet disambung",
    wallet_disconnected: "Terputus",
    theme_dark: "Mod gelap",
    theme_light: "Mod cerah",
  },
  bn: {
    nav_round: "রাউন্ড",
    nav_how: "কিভাবে কাজ করে",
    nav_trust: "স্বচ্ছতা",
    status_open: "রাউন্ড খোলা",
    status_closed: "রাউন্ড বন্ধ",
    status_need_wallet: "ওয়ালেট প্রয়োজন",
    purchase_title: "টিকিট ক্রয়",
    buy_button: "টিকিট কিনুন",
    draw_button: "ড্র সমাপ্ত করুন",
    history_title: "রাউন্ড ইতিহাস",
    delivery_title: "দুবাই থেকে পাবলিক ডেলিভারি ট্র্যাক",
    shipping_title: "ডেলিভারি ঠিকানা (বিজয়ী)",
    connect_wallet: "ওয়ালেট সংযুক্ত করুন",
    wallet_connected: "ওয়ালেট সংযুক্ত",
    wallet_disconnected: "বিচ্ছিন্ন",
    theme_dark: "ডার্ক মোড",
    theme_light: "লাইট মোড",
  },
  ur: {
    nav_round: "راؤنڈ",
    nav_how: "یہ کیسے کام کرتا ہے",
    nav_trust: "شفافیت",
    status_open: "راؤنڈ کھلا ہے",
    status_closed: "راؤنڈ بند ہے",
    status_need_wallet: "والیٹ ضروری ہے",
    purchase_title: "ٹکٹ خریداری",
    buy_button: "ٹکٹ خریدیں",
    draw_button: "قرعہ مکمل کریں",
    history_title: "راؤنڈ ہسٹری",
    delivery_title: "دبئی سے عوامی ڈیلیوری ٹریک",
    shipping_title: "ڈیلیوری پتہ (فاتح)",
    connect_wallet: "والیٹ کنیکٹ کریں",
    wallet_connected: "والیٹ کنیکٹڈ",
    wallet_disconnected: "منقطع",
    theme_dark: "ڈارک موڈ",
    theme_light: "لائٹ موڈ",
  },
  ta: {
    nav_round: "சுற்று",
    nav_how: "இது எப்படி செயல்படுகிறது",
    nav_trust: "தெளிவு",
    status_open: "சுற்று திறந்துள்ளது",
    status_closed: "சுற்று மூடப்பட்டது",
    status_need_wallet: "வாலெட் தேவை",
    purchase_title: "டிக்கெட் வாங்குதல்",
    buy_button: "டிக்கெட் வாங்க",
    draw_button: "டிரா முடிக்க",
    history_title: "சுற்று வரலாறு",
    delivery_title: "துபாயில் இருந்து பொது டெலிவரி டிராக்",
    shipping_title: "டெலிவரி முகவரி (வெற்றியாளர்)",
    connect_wallet: "வாலெட் இணைக்கவும்",
    wallet_connected: "வாலெட் இணைந்தது",
    wallet_disconnected: "இணைக்கப்படவில்லை",
    theme_dark: "டார்க் மோடு",
    theme_light: "லைட் மோடு",
  },
};

const MESSAGES = {
  en: {
    msg_wallet_required: "Connect wallet before buying tickets.",
    msg_connect_wallet_first: "Connect your wallet first.",
    msg_network_wrong: "Switch wallet network to Ethereum Mainnet.",
    msg_backend_offline: "Backend API is unavailable. Check apiBaseUrl and server status.",
    msg_no_tickets_left: "No tickets left in this round.",
    msg_tx_submitted: "USDT transaction sent: {hash}",
    msg_tx_confirming: "Waiting for on-chain confirmation...",
    msg_tx_failed: "Transaction failed. Please check wallet activity and retry.",
    msg_purchase_success: "Purchase confirmed: {count} ticket(s).",
    msg_finalize_pending: "Draw is not ready yet. Blocks left: {blocks}.",
    msg_finalize_done: "Round #{round} finalized. Winner ticket #{ticket}.",
    msg_finalize_noop: "No sold-out round is ready for finalization.",
    msg_error_prefix: "Error: {message}",
    msg_wallet_connected: "Wallet connected. You can pay in USDT.",
    msg_wallet_disconnected: "Wallet disconnected.",
    msg_tx_hash: "Last transaction hash",
    msg_round_wait: "Waiting for sold-out to finalize draw.",
    msg_delivery_wait: "Delivery timeline appears after winner confirmation.",
  },
  ru: {
    msg_wallet_required: "Подключи кошелек перед покупкой билетов.",
    msg_connect_wallet_first: "Сначала подключи кошелек.",
    msg_network_wrong: "Переключи сеть кошелька на Ethereum Mainnet.",
    msg_backend_offline: "Backend API недоступен. Проверь apiBaseUrl и сервер.",
    msg_no_tickets_left: "В этом раунде больше нет билетов.",
    msg_tx_submitted: "USDT транзакция отправлена: {hash}",
    msg_tx_confirming: "Ожидаем подтверждение в сети...",
    msg_tx_failed: "Транзакция не прошла. Проверь кошелек и повтори.",
    msg_purchase_success: "Покупка подтверждена: {count} билет(ов).",
    msg_finalize_pending: "Розыгрыш еще недоступен. Осталось блоков: {blocks}.",
    msg_finalize_done: "Раунд #{round} завершен. Победил билет #{ticket}.",
    msg_finalize_noop: "Нет sold-out раунда, готового к завершению.",
    msg_error_prefix: "Ошибка: {message}",
    msg_wallet_connected: "Кошелек подключен. Можно оплачивать в USDT.",
    msg_wallet_disconnected: "Кошелек отключен.",
    msg_tx_hash: "Последний tx hash",
    msg_round_wait: "Ожидаем sold-out для завершения розыгрыша.",
    msg_delivery_wait: "Шкала доставки появится после подтверждения победителя.",
  },
};

const ui = {
  languageSelect: document.getElementById("languageSelect"),
  themeToggle: document.getElementById("themeToggle"),
  walletButton: document.getElementById("walletButton"),
  roundStatus: document.getElementById("roundStatus"),
  heroTitle: document.getElementById("heroTitle"),
  heroNote: document.getElementById("heroNote"),
  ticketPrice: document.getElementById("ticketPrice"),
  ticketCurrency: document.getElementById("ticketCurrency"),
  ticketsSold: document.getElementById("ticketsSold"),
  ticketsTotal: document.getElementById("ticketsTotal"),
  ticketsRemaining: document.getElementById("ticketsRemaining"),
  poolValue: document.getElementById("poolValue"),
  soldPercent: document.getElementById("soldPercent"),
  roundLabel: document.getElementById("roundLabel"),
  progressText: document.getElementById("progressText"),
  progressFill: document.getElementById("progressFill"),
  purchaseForm: document.getElementById("purchaseForm"),
  purchaseButton: document.getElementById("purchaseButton"),
  ticketCountInput: document.getElementById("ticketCount"),
  qtyChips: Array.from(document.querySelectorAll(".qty-chip")),
  purchaseHint: document.getElementById("purchaseHint"),
  buyChance: document.getElementById("buyChance"),
  remainingInline: document.getElementById("remainingInline"),
  lastTxHash: document.getElementById("lastTxHash"),
  ticketList: document.getElementById("ticketList"),
  drawRule: document.getElementById("drawRule"),
  drawButton: document.getElementById("drawButton"),
  drawResult: document.getElementById("drawResult"),
  historyList: document.getElementById("historyList"),
  deliveryTimeline: document.getElementById("deliveryTimeline"),
  deliveryProgressFill: document.getElementById("deliveryProgressFill"),
  deliveryProgressText: document.getElementById("deliveryProgressText"),
  chainName: document.getElementById("chainName"),
  tokenName: document.getElementById("tokenName"),
  contractAddress: document.getElementById("contractAddress"),
  walletStatus: document.getElementById("walletStatus"),
  shippingFullName: document.getElementById("shippingFullName"),
  shippingPhone: document.getElementById("shippingPhone"),
  shippingCountry: document.getElementById("shippingCountry"),
  shippingCity: document.getElementById("shippingCity"),
  shippingAddressLine1: document.getElementById("shippingAddressLine1"),
  shippingAddressLine2: document.getElementById("shippingAddressLine2"),
  shippingPostalCode: document.getElementById("shippingPostalCode"),
};

const state = {
  config: {
    ...DEFAULT_CONFIG,
    ...(window.WINSPOT_CONFIG || {}),
  },
  language: "en",
  theme: "light",
  walletAddress: null,
  provider: null,
  signer: null,
  round: null,
  history: [],
  delivery: null,
  isBusy: false,
};

function readStorage(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function writeStorage(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function t(key, vars = {}) {
  const dictionary = UI_TRANSLATIONS[state.language] || UI_TRANSLATIONS.en;
  const fallback = UI_TRANSLATIONS.en[key] || key;
  const template = dictionary[key] || fallback;
  return Object.entries(vars).reduce(
    (value, [name, replacement]) => value.replaceAll(`{${name}}`, String(replacement)),
    template
  );
}

function message(key, vars = {}) {
  const dictionary = MESSAGES[state.language] || MESSAGES.en;
  const fallback = MESSAGES.en[key] || key;
  const template = dictionary[key] || fallback;
  return Object.entries(vars).reduce(
    (value, [name, replacement]) => value.replaceAll(`{${name}}`, String(replacement)),
    template
  );
}

function shortAddress(address) {
  if (!address || address.length < 10) {
    return address || "";
  }
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

function shortHash(hash) {
  if (!hash || hash.length < 14) {
    return hash || "";
  }
  return `${hash.slice(0, 10)}...${hash.slice(-8)}`;
}

function formatUSD(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

function formatUSDTFromMicro(amountMicro) {
  const value = Number(amountMicro) / 1_000_000;
  return `${formatUSD(value)} USDT`;
}

function clampTicketCount(value) {
  const parsed = Number.isFinite(value) ? Math.floor(value) : 1;
  const max = Math.max(1, Number(state.config.maxTicketsPerPurchase) || 20);
  return Math.min(Math.max(parsed, 1), max);
}

function getRemainingTickets() {
  if (!state.round) {
    return state.config.totalTickets;
  }
  return Math.max(state.round.remaining_tickets, 0);
}

function getCurrentInputCount() {
  const remaining = getRemainingTickets();
  if (remaining <= 0) {
    return 0;
  }
  return Math.min(clampTicketCount(Number(ui.ticketCountInput.value)), remaining);
}

function setBusy(isBusy) {
  state.isBusy = isBusy;
  ui.purchaseButton.disabled = isBusy || getRemainingTickets() === 0;
  ui.drawButton.disabled = isBusy || !state.round || state.round.state !== "sold_out";
}

function updateQtyChips() {
  const selected = Number(ui.ticketCountInput.value);
  ui.qtyChips.forEach((chip) => {
    const chipQty = Number(chip.dataset.qty);
    chip.classList.toggle("active", chipQty === selected);
  });
}

function clearNode(node) {
  if (!node) {
    return;
  }
  while (node.firstChild) {
    node.removeChild(node.firstChild);
  }
}

function appendRow(container, lines) {
  const wrapper = document.createElement("div");
  wrapper.className = container.id === "historyList" ? "history-item" : "ticket-item";

  lines.forEach((line, index) => {
    const element = document.createElement(index === 0 ? "strong" : "div");
    element.textContent = line;
    wrapper.appendChild(element);
  });
  container.appendChild(wrapper);
}

function setDrawMessage(text, mode = "default") {
  ui.drawResult.className = "draw-result";
  if (mode === "win") {
    ui.drawResult.classList.add("win");
  }
  if (mode === "alert") {
    ui.drawResult.classList.add("alert");
  }

  clearNode(ui.drawResult);
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  ui.drawResult.appendChild(paragraph);
}

function resolveInitialTheme() {
  const stored = readStorage(storageKeys.theme, null);
  if (stored === "dark" || stored === "light") {
    return stored;
  }
  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }
  return "light";
}

function resolveInitialLanguage() {
  const stored = readStorage(storageKeys.language, null);
  if (stored && LANGUAGE_OPTIONS.some((item) => item.code === stored)) {
    return stored;
  }
  const browser = (navigator.language || "en").slice(0, 2).toLowerCase();
  if (LANGUAGE_OPTIONS.some((item) => item.code === browser)) {
    return browser;
  }
  return "en";
}

function applyTheme() {
  document.documentElement.setAttribute("data-theme", state.theme);
  ui.themeToggle.textContent = state.theme === "dark" ? t("theme_light") : t("theme_dark");
}

function applyStaticTranslations() {
  document.documentElement.lang = state.language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.getAttribute("data-i18n");
    const dictionary = UI_TRANSLATIONS[state.language] || UI_TRANSLATIONS.en;
    if (key && dictionary[key]) {
      element.textContent = dictionary[key];
    }
  });
  ui.themeToggle.textContent = state.theme === "dark" ? t("theme_light") : t("theme_dark");
}

function populateLanguageSelect() {
  clearNode(ui.languageSelect);
  LANGUAGE_OPTIONS.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.code;
    option.textContent = item.label;
    ui.languageSelect.appendChild(option);
  });
  ui.languageSelect.value = state.language;
}

function mergeBackendConfig(configPayload) {
  if (!configPayload || typeof configPayload !== "object") {
    return;
  }
  state.config = {
    ...state.config,
    chainId: Number(configPayload.chain_id ?? state.config.chainId),
    chainName: configPayload.chain_name ?? state.config.chainName,
    tokenSymbol: configPayload.token_symbol ?? state.config.tokenSymbol,
    tokenStandard: configPayload.token_standard ?? state.config.tokenStandard,
    tokenAddress: configPayload.usdt_contract ?? state.config.tokenAddress,
    treasuryAddress: configPayload.treasury_address ?? state.config.treasuryAddress,
    totalTickets: Number(configPayload.total_tickets ?? state.config.totalTickets),
    ticketPrice: Number(configPayload.ticket_price_usdt ?? state.config.ticketPrice),
    ticketPriceMicro: Number(configPayload.ticket_price_micro ?? state.config.ticketPriceMicro),
    maxTicketsPerPurchase: Number(
      configPayload.max_tickets_per_purchase ?? state.config.maxTicketsPerPurchase
    ),
    shippingStartDate: configPayload.shipping_start_date ?? state.config.shippingStartDate,
  };
}

function apiBase() {
  const raw = (state.config.apiBaseUrl || "/api/v1").trim();
  return raw.endsWith("/") ? raw.slice(0, -1) : raw;
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${apiBase()}${path}`, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    body: options.body,
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload?.detail || payload?.message || `HTTP ${response.status}`;
    throw new Error(detail);
  }
  return payload;
}

async function refreshData() {
  const walletQuery = state.walletAddress ? `?wallet=${encodeURIComponent(state.walletAddress)}` : "";
  const [roundPayload, historyPayload] = await Promise.all([
    apiRequest(`/round/current${walletQuery}`),
    apiRequest("/round/history?limit=6"),
  ]);

  state.round = roundPayload;
  state.history = historyPayload.items || [];

  const deliveryRound =
    state.round?.state === "drawn"
      ? state.round.round_number
      : state.history.length
        ? state.history[0].round_number
        : null;

  if (deliveryRound) {
    state.delivery = await apiRequest(`/round/${deliveryRound}/shipping`);
  } else {
    state.delivery = null;
  }

  renderAll();
}

function renderConfig() {
  ui.heroTitle.textContent = `${state.config.prizeName}`;
  ui.heroNote.textContent = `${state.config.totalTickets} билетов · ${formatUSD(state.config.ticketPrice)} · Приз: ${state.config.prizeName}`;
  ui.chainName.textContent = state.config.chainName;
  ui.tokenName.textContent = `${state.config.tokenSymbol} (${state.config.tokenStandard})`;
  ui.contractAddress.textContent = state.config.contractAddress;
}

function renderWallet() {
  const connected = Boolean(state.walletAddress);
  ui.walletStatus.textContent = connected ? shortAddress(state.walletAddress) : t("wallet_disconnected");
  ui.walletButton.textContent = connected ? t("wallet_connected") : t("connect_wallet");
  ui.walletButton.classList.toggle("connected", connected);
}

function renderOverview() {
  const sold = state.round?.sold_tickets ?? 0;
  const total = state.round?.total_tickets ?? state.config.totalTickets;
  const remaining = Math.max(total - sold, 0);
  const progress = total > 0 ? (sold / total) * 100 : 0;
  const poolMicro = sold * state.config.ticketPriceMicro;

  ui.ticketPrice.textContent = formatUSD(state.config.ticketPrice);
  ui.ticketCurrency.textContent = state.config.tokenSymbol;
  ui.ticketsSold.textContent = String(sold);
  ui.ticketsTotal.textContent = String(total);
  ui.ticketsRemaining.textContent = String(remaining);
  ui.remainingInline.textContent = String(remaining);
  ui.poolValue.textContent = formatUSD(poolMicro / 1_000_000);
  ui.soldPercent.textContent = `${Math.round(progress)}%`;
  ui.roundLabel.textContent = `Раунд #${state.round?.round_number ?? 1}`;
  ui.progressText.textContent = `Продано ${sold} из ${total} билетов`;
  ui.progressFill.style.width = `${Math.min(progress, 100)}%`;
}

function renderPurchaseHint() {
  const remaining = getRemainingTickets();
  if (remaining <= 0) {
    ui.purchaseHint.textContent = "Билеты распроданы. Запусти завершение розыгрыша.";
    ui.buyChance.textContent = "~0%";
    updateQtyChips();
    return;
  }

  const count = getCurrentInputCount();
  const chance = (count / (state.round?.total_tickets || state.config.totalTickets)) * 100;
  ui.ticketCountInput.value = String(count);
  ui.purchaseHint.textContent = `Итог: ${formatUSDTFromMicro(count * state.config.ticketPriceMicro)}`;
  ui.buyChance.textContent = `~${chance.toFixed(chance < 10 ? 1 : 0)}%`;
  updateQtyChips();
}

function renderTicketList() {
  clearNode(ui.ticketList);
  const walletTickets = state.round?.wallet_tickets || [];
  if (!walletTickets.length) {
    ui.ticketList.className = "ticket-list empty";
    ui.ticketList.textContent = "Ваши билеты этого раунда пока отсутствуют.";
    return;
  }

  ui.ticketList.className = "ticket-list";
  walletTickets.slice(0, 12).forEach((item) => {
    appendRow(ui.ticketList, [
      `#${String(item.serial).padStart(3, "0")}`,
      `Раунд #${state.round.round_number}`,
      new Date(item.created_at).toLocaleString(),
    ]);
  });
}

function renderHistory() {
  clearNode(ui.historyList);
  if (!state.history.length) {
    ui.historyList.className = "history-list empty";
    ui.historyList.textContent = "История пока пуста.";
    return;
  }

  ui.historyList.className = "history-list";
  state.history.forEach((item) => {
    const winnerId = item.winner_ticket_serial ? `#${String(item.winner_ticket_serial).padStart(3, "0")}` : "-";
    appendRow(ui.historyList, [
      `Раунд #${item.round_number}`,
      `Победитель: ${winnerId}`,
      `Кошелек: ${shortAddress(item.winner_wallet || "")}`,
      `Пул: ${formatUSD((item.sold_tickets * item.ticket_price_micro) / 1_000_000)} USDT`,
    ]);
  });
}

function renderDelivery() {
  clearNode(ui.deliveryTimeline);
  if (!state.delivery || !state.delivery.items || !state.delivery.items.length) {
    ui.deliveryTimeline.className = "history-list empty";
    ui.deliveryTimeline.textContent = message("msg_delivery_wait");
    ui.deliveryProgressFill.style.width = "0%";
    ui.deliveryProgressText.textContent = message("msg_delivery_wait");
    return;
  }

  ui.deliveryTimeline.className = "history-list";
  ui.deliveryProgressFill.style.width = `${state.delivery.progress_percent || 0}%`;
  ui.deliveryProgressText.textContent = `Раунд #${state.delivery.round_number}: ${state.delivery.progress_percent || 0}%`;

  state.delivery.items.forEach((item) => {
    const statusLabel =
      item.status === "completed" ? "Completed" : item.status === "in_progress" ? "In progress" : "Pending";
    appendRow(ui.deliveryTimeline, [
      `${item.step_order}. ${item.title}`,
      item.detail,
      `${item.planned_date} · ${statusLabel}`,
    ]);
  });
}

function renderControls() {
  const remaining = getRemainingTickets();
  const soldOut = remaining <= 0;
  const connected = Boolean(state.walletAddress);

  ui.purchaseButton.disabled = state.isBusy || soldOut;
  ui.ticketCountInput.disabled = state.isBusy || soldOut;
  ui.qtyChips.forEach((chip) => {
    chip.disabled = state.isBusy || soldOut;
  });
  ui.drawButton.disabled = state.isBusy || state.round?.state !== "sold_out";

  if (state.round?.state === "sold_out") {
    ui.roundStatus.textContent = t("status_closed");
    ui.roundStatus.classList.add("soldout");
    ui.drawRule.textContent = "Раунд sold-out. Нажми «Завершить розыгрыш» после достижения draw block.";
  } else if (state.config.walletRequired && !connected) {
    ui.roundStatus.textContent = t("status_need_wallet");
    ui.roundStatus.classList.remove("soldout");
    ui.drawRule.textContent = message("msg_round_wait");
  } else {
    ui.roundStatus.textContent = t("status_open");
    ui.roundStatus.classList.remove("soldout");
    ui.drawRule.textContent = "Розыгрыш доступен после продажи всех 100 билетов.";
  }
}

function renderAll() {
  applyStaticTranslations();
  renderConfig();
  renderWallet();
  renderOverview();
  renderPurchaseHint();
  renderTicketList();
  renderHistory();
  renderDelivery();
  renderControls();
}

function collectShipping() {
  const payload = {
    full_name: ui.shippingFullName.value.trim(),
    phone: ui.shippingPhone.value.trim(),
    country: ui.shippingCountry.value.trim(),
    city: ui.shippingCity.value.trim(),
    address_line1: ui.shippingAddressLine1.value.trim(),
    address_line2: ui.shippingAddressLine2.value.trim(),
    postal_code: ui.shippingPostalCode.value.trim(),
  };

  if (!payload.full_name || !payload.phone || !payload.country || !payload.city || !payload.address_line1) {
    throw new Error("Заполни обязательные поля доставки.");
  }
  return payload;
}

async function connectWallet() {
  if (!window.ethereum || !window.ethers) {
    throw new Error("Web3 wallet is not available in this browser.");
  }

  const provider = new window.ethers.BrowserProvider(window.ethereum);
  await provider.send("eth_requestAccounts", []);
  const network = await provider.getNetwork();
  const chainId = Number(network.chainId);
  if (chainId !== Number(state.config.chainId)) {
    throw new Error(message("msg_network_wrong"));
  }

  const signer = await provider.getSigner();
  const address = (await signer.getAddress()).toLowerCase();

  state.provider = provider;
  state.signer = signer;
  state.walletAddress = address;
  renderWallet();
  setDrawMessage(message("msg_wallet_connected"), "alert");
  await refreshData();
}

async function onWalletClick() {
  try {
    await connectWallet();
  } catch (error) {
    setDrawMessage(message("msg_error_prefix", { message: error.message || String(error) }), "alert");
  }
}

async function buyTickets(event) {
  event.preventDefault();
  if (state.isBusy) {
    return;
  }

  if (state.config.walletRequired && !state.walletAddress) {
    setDrawMessage(message("msg_wallet_required"), "alert");
    return;
  }
  if (!state.round || state.round.state !== "open") {
    setDrawMessage(message("msg_no_tickets_left"), "alert");
    return;
  }

  const remaining = getRemainingTickets();
  if (remaining <= 0) {
    setDrawMessage(message("msg_no_tickets_left"), "alert");
    return;
  }

  const ticketCount = getCurrentInputCount();
  const shipping = collectShipping();

  try {
    setBusy(true);
    const usdt = new window.ethers.Contract(state.config.tokenAddress, USDT_ABI, state.signer);
    const amount = BigInt(state.config.ticketPriceMicro) * BigInt(ticketCount);

    const tx = await usdt.transfer(state.config.treasuryAddress, amount);
    ui.lastTxHash.textContent = `${message("msg_tx_hash")}: ${tx.hash}`;
    setDrawMessage(message("msg_tx_submitted", { hash: shortHash(tx.hash) }), "alert");

    await tx.wait(1);
    setDrawMessage(message("msg_tx_confirming"), "alert");

    await apiRequest("/purchases", {
      method: "POST",
      body: JSON.stringify({
        wallet_address: state.walletAddress,
        tx_hash: tx.hash,
        ticket_count: ticketCount,
        language: state.language,
        shipping,
      }),
    });

    setDrawMessage(message("msg_purchase_success", { count: ticketCount }), "default");
    await refreshData();
  } catch (error) {
    setDrawMessage(
      message("msg_error_prefix", { message: error?.message || message("msg_tx_failed") }),
      "alert"
    );
  } finally {
    setBusy(false);
    renderControls();
  }
}

async function finalizeDraw() {
  if (state.isBusy) {
    return;
  }
  try {
    setBusy(true);
    const result = await apiRequest("/round/finalize", { method: "POST" });
    if (result.status === "pending") {
      setDrawMessage(message("msg_finalize_pending", { blocks: result.blocks_left ?? 0 }), "alert");
    } else if (result.status === "completed") {
      setDrawMessage(
        message("msg_finalize_done", {
          round: result.round_number,
          ticket: String(result.winner_ticket_serial).padStart(3, "0"),
        }),
        "win"
      );
    } else {
      setDrawMessage(message("msg_finalize_noop"), "alert");
    }
    await refreshData();
  } catch (error) {
    setDrawMessage(message("msg_error_prefix", { message: error.message || String(error) }), "alert");
  } finally {
    setBusy(false);
    renderControls();
  }
}

function onThemeToggle() {
  state.theme = state.theme === "dark" ? "light" : "dark";
  writeStorage(storageKeys.theme, state.theme);
  applyTheme();
}

function onLanguageChange() {
  state.language = ui.languageSelect.value;
  writeStorage(storageKeys.language, state.language);
  applyStaticTranslations();
  renderAll();
}

function setupWalletListeners() {
  if (!window.ethereum || typeof window.ethereum.on !== "function") {
    return;
  }

  window.ethereum.on("accountsChanged", async (accounts) => {
    if (!accounts || !accounts.length) {
      state.walletAddress = null;
      state.provider = null;
      state.signer = null;
      renderWallet();
      setDrawMessage(message("msg_wallet_disconnected"), "alert");
      renderControls();
      return;
    }
    state.walletAddress = accounts[0].toLowerCase();
    try {
      await refreshData();
    } catch {
      renderAll();
    }
  });

  window.ethereum.on("chainChanged", () => {
    window.location.reload();
  });
}

async function bootstrap() {
  state.theme = resolveInitialTheme();
  state.language = resolveInitialLanguage();

  applyTheme();
  populateLanguageSelect();
  applyStaticTranslations();
  renderAll();

  ui.languageSelect.addEventListener("change", onLanguageChange);
  ui.themeToggle.addEventListener("click", onThemeToggle);
  ui.walletButton.addEventListener("click", onWalletClick);
  ui.purchaseForm.addEventListener("submit", buyTickets);
  ui.drawButton.addEventListener("click", finalizeDraw);
  ui.ticketCountInput.addEventListener("input", renderPurchaseHint);
  ui.qtyChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      ui.ticketCountInput.value = chip.dataset.qty || "1";
      renderPurchaseHint();
    });
  });
  setupWalletListeners();

  try {
    const backendConfig = await apiRequest("/public/config");
    mergeBackendConfig(backendConfig);
    await refreshData();
  } catch (error) {
    setDrawMessage(
      message("msg_error_prefix", { message: `${message("msg_backend_offline")} (${error.message || "n/a"})` }),
      "alert"
    );
    renderAll();
  }
}

bootstrap();
