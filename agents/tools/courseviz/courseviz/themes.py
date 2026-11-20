"""Palettes are presentation only; never encode a different dataset."""
THEMES = {
 'paper': dict(bg='#f6f8fc',surface='#ffffff',ink='#14253d',muted='#4a5c73',line='#c3cddd',accent='#195caf',palette=['#195caf','#a14010','#17695b','#853781','#66510b','#4e4da2']),
 'midnight': dict(bg='#101b2d',surface='#192940',ink='#f0f5ff',muted='#b8c9df',line='#4e6581',accent='#79c7ff',palette=['#79c7ff','#ffc18a','#81dcc4','#efa4e1','#e6d87c','#b7b0ff']),
 'blueprint': dict(bg='#102c48',surface='#153958',ink='#f1f8ff',muted='#b5d6ed',line='#547a96',accent='#8de5ff',palette=['#8de5ff','#ffcb9a','#a3e6bc','#e6b4ef','#f3e69d','#bfc7ff']),
 'warm': dict(bg='#faf4e8',surface='#fffdf6',ink='#362a27',muted='#675851',line='#d5c7b3',accent='#9a3f24',palette=['#9a3f24','#236558','#62519c','#8b4b70','#725c08','#255a85']),
 'mono': dict(bg='#ffffff',surface='#f5f5f5',ink='#111111',muted='#505050',line='#a0a0a0',accent='#111111',palette=['#111111','#444444','#777777','#222222','#555555','#888888']),
}
for _theme in THEMES.values():
    _theme['font'] = 'DejaVu Sans, Liberation Sans, Arial, sans-serif'
