import subprocess

def test():
    subprocess.run(['/usr/bin/fontforge','svgs2ttf','font.json', '/home/kdh/jolsul/HandWriteFont_BE/handwritefont_be/media/admin@admin.com/FirstTest5/gen_glyphs/svg_glyphs', '/home/kdh/jolsul/HandWriteFont_BE/handwritefont_be/media/admin@admin.com/FirstTest5/gen_glyphs/output', 'FirstTest5_4'])
