"""Sticker-style product illustrations for Digittouch Finds guides.
Each value is the inner SVG markup for viewBox 0 0 200 160. Ink outline, flat fills."""

INK = "#1D1B20"
S = f'stroke="{INK}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"'

ART = {
"slippers": f'''<g {S}>
<path d="M52 24 C78 24 90 48 88 84 C86 120 80 148 60 148 C40 148 32 120 30 84 C28 48 30 24 52 24Z" fill="#F7B7C5"/>
<path d="M132 18 C158 18 170 42 168 78 C166 114 160 142 140 142 C120 142 112 114 110 78 C108 42 110 18 132 18Z" fill="#F7B7C5"/>
<path d="M30 62 C34 40 46 34 58 34 C70 34 84 40 88 62 C70 72 48 72 30 62Z" fill="#FFF8EF"/>
<path d="M110 56 C114 34 126 28 138 28 C150 28 164 34 168 56 C150 66 128 66 110 56Z" fill="#FFF8EF"/></g>
<g fill="{INK}"><circle cx="46" cy="50" r="3.5"/><circle cx="60" cy="56" r="3.5"/><circle cx="72" cy="48" r="3.5"/><circle cx="126" cy="44" r="3.5"/><circle cx="140" cy="50" r="3.5"/><circle cx="152" cy="42" r="3.5"/></g>''',

"lamp": f'''<g {S}>
<path d="M48 148 H112" fill="none"/>
<path d="M150 148 V28 H100 V44" fill="none"/>
<rect x="134" y="140" width="32" height="10" rx="4" fill="{INK}"/>
<path d="M62 70 C62 46 138 46 138 70 Z" fill="#E4572E"/>
<rect x="56" y="104" width="62" height="44" rx="8" fill="#FFF8EF"/>
<path d="M56 116 H118" fill="none"/></g>
<path d="M78 80 L72 94 M100 82 V96 M122 80 L128 94" stroke="#E4572E" stroke-width="5" stroke-linecap="round" fill="none"/>''',

"candle": f'''<g {S}>
<path d="M58 54 H142 V140 C142 146 138 150 132 150 H68 C62 150 58 146 58 140Z" fill="#CDEFDD"/>
<rect x="70" y="86" width="60" height="40" rx="6" fill="#FFF8EF"/>
<path d="M100 54 V40" fill="none"/>
<path d="M100 14 C112 26 110 40 100 40 C90 40 88 26 100 14Z" fill="#FFC93C"/></g>
<path d="M100 92 L114 116 H86Z" fill="#5BB57E" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/><path d="M100 116 V122" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>''',

"mask": f'''<g {S}>
<path d="M14 78 C40 70 40 70 30 72" fill="none"/>
<path d="M14 80 H34 M166 80 H186" fill="none"/>
<path d="M34 64 C34 44 92 44 100 62 C108 44 166 44 166 64 C166 100 120 112 100 92 C80 112 34 100 34 64Z" fill="#E4D8FF"/></g>
<g stroke="{INK}" stroke-width="5" stroke-linecap="round" fill="none"><path d="M56 76 C64 84 76 84 84 76"/><path d="M116 76 C124 84 136 84 144 76"/></g>''',

"tumbler": f'''<g {S}>
<path d="M118 6 L104 40" fill="none"/>
<path d="M62 40 H138 L130 150 H70 Z" fill="#7FC8F8"/>
<rect x="56" y="30" width="88" height="16" rx="6" fill="#FFF8EF"/>
<path d="M134 64 C166 64 166 116 132 116" fill="none" stroke-width="10"/>
<path d="M134 64 C166 64 166 116 132 116" fill="none" stroke="#7FC8F8" stroke-width="2"/>
<path d="M74 88 H126" fill="none"/></g>''',

"pouch": f'''<g {S}>
<path d="M22 70 H178 V140 C178 146 174 150 168 150 H32 C26 150 22 146 22 140Z" fill="#FFC93C"/>
<path d="M22 70 H178" fill="none"/>
<rect x="44" y="30" width="26" height="48" rx="6" fill="#FFF8EF"/>
<rect x="80" y="20" width="22" height="58" rx="10" fill="#F7B7C5"/>
<rect x="112" y="36" width="34" height="42" rx="8" fill="#CDEFDD"/>
<rect x="150" y="44" width="16" height="34" rx="4" fill="#E4D8FF"/></g>
<path d="M92 104 H108" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>''',

"bottle": f'''<g {S}>
<path d="M100 40 V20 H128" fill="none"/>
<rect x="88" y="40" width="24" height="16" rx="3" fill="{INK}"/>
<path d="M70 56 H130 C136 56 140 60 140 66 V142 C140 148 136 152 130 152 H70 C64 152 60 148 60 142 V66 C60 60 64 56 70 56Z" fill="#A8D5BA"/>
<rect x="74" y="84" width="52" height="46" rx="6" fill="#FFF8EF"/></g>
<path d="M86 100 H114 M86 112 H106" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>''',

"cuff": f'''<g {S}>
<path d="M44 92 C44 48 156 48 156 92 C156 120 132 132 118 130 M82 130 C68 132 44 120 44 92" fill="none" stroke-width="22"/>
<path d="M44 92 C44 48 156 48 156 92 C156 120 132 132 118 130 M82 130 C68 132 44 120 44 92" fill="none" stroke="#F2B53A" stroke-width="12"/></g>
<path d="M70 64 C80 58 92 56 100 56" stroke="#FFF8EF" stroke-width="5" stroke-linecap="round" fill="none"/>''',

"plants": f'''<g {S}>
<path d="M30 106 H74 L68 148 H36Z" fill="#E4572E"/>
<path d="M84 96 H128 L122 148 H90Z" fill="#E4572E"/>
<path d="M138 110 H174 L169 148 H143Z" fill="#E4572E"/>
<path d="M52 106 C40 80 46 66 52 60 C58 66 64 80 52 106Z" fill="#5BB57E"/>
<path d="M106 96 C84 82 84 60 88 52 C100 60 108 76 106 96Z M106 96 C120 74 132 70 140 70 C136 84 126 94 106 96Z" fill="#5BB57E"/>
<circle cx="156" cy="96" r="14" fill="#5BB57E"/></g>''',

"bangles": f'''<g fill="none">
<circle cx="78" cy="84" r="46" stroke="{INK}" stroke-width="22"/>
<circle cx="78" cy="84" r="46" stroke="#F7B7C5" stroke-width="12"/>
<circle cx="124" cy="84" r="46" stroke="{INK}" stroke-width="22"/>
<circle cx="124" cy="84" r="46" stroke="#7FC8F8" stroke-width="12"/></g>''',

"makeup": f'''<g {S}>
<rect x="34" y="76" width="34" height="74" rx="5" fill="{INK}"/>
<rect x="38" y="52" width="26" height="28" rx="3" fill="#F2B53A"/>
<path d="M40 52 V30 L62 20 V52Z" fill="#E4572E"/>
<circle cx="132" cy="104" r="44" fill="#F7B7C5"/>
<circle cx="132" cy="104" r="28" fill="#FFF8EF"/></g>
<circle cx="132" cy="104" r="14" fill="#F2B53A" stroke="{INK}" stroke-width="4"/>''',

"gift": f'''<g {S}>
<rect x="36" y="64" width="128" height="86" rx="8" fill="#E4572E"/>
<rect x="28" y="46" width="144" height="26" rx="6" fill="#FFC93C"/>
<path d="M100 46 V150" fill="none"/>
<path d="M100 46 C80 14 52 30 72 46 M100 46 C120 14 148 30 128 46" fill="#FFF8EF"/></g>''',
}


def svg(name, label):
    return (f'<svg viewBox="0 0 200 160" role="img" aria-label="{label}" '
            f'xmlns="http://www.w3.org/2000/svg">{ART[name]}</svg>')
