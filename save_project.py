# save_project.py
import os
import datetime

def export_entire_project():
    """تصدير جميع أكواد المشروع في ملف واحد منظم"""
    
    project_name = "SG_Correspondance"
    output_file = f"{project_name}_FULL_CODE.txt"
    
    # تجاهل هذه الملفات والمجلدات
    IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'env', 'node_modules'}
    IGNORE_FILES = {'.pyc', '.db', '.sqlite3', '.jpg', '.png', '.ico'}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # رأس الملف
        f.write("=" * 80 + "\n")
        f.write(f"📁 مشروع: {project_name}\n")
        f.write(f"📅 تاريخ التصدير: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"📊 تم التصدير بواسطة: save_project.py\n")
        f.write("=" * 80 + "\n\n")
        
        total_files = 0
        
        for root, dirs, files in os.walk('.'):
            # تجاهل المجلدات غير المرغوبة
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                # تجاهل الملفات غير المرغوبة
                if any(file.endswith(ext) for ext in IGNORE_FILES):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path)
                
                # تخطى الملف نفسه
                if file == 'save_project.py' or file == output_file:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file_content:
                        content = file_content.read()
                        
                        # كتابة معلومات الملف
                        f.write("\n" + "=" * 80 + "\n")
                        f.write(f"📄 الملف: {rel_path}\n")
                        f.write(f"📏 الحجم: {len(content):,} حرف\n")
                        f.write(f"📁 المسار: {file_path}\n")
                        f.write("=" * 80 + "\n\n")
                        
                        # كتابة المحتوى
                        f.write(content)
                        
                        # إذا كان الملف كبيراً، أضف فاصل
                        if len(content) > 1000:
                            f.write(f"\n{'='*80}\n")
                        
                        total_files += 1
                        
                except Exception as e:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"❌ خطأ في قراءة الملف: {rel_path}\n")
                    f.write(f"📛 الخطأ: {str(e)}\n")
                    f.write(f"{'='*80}\n\n")
        
        # تذييل الملف
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"✅ تم تصدير {total_files} ملف بنجاح!\n")
        f.write(f"💾 اسم الملف: {output_file}\n")
        f.write(f"🕒 وقت التنفيذ: {datetime.datetime.now().strftime('%H:%M:%S')}\n")
        f.write("=" * 80 + "\n")
    
    print(f"✅ تم حفظ جميع الأكواد في: {output_file}")
    print(f"📊 عدد الملفات: {total_files}")
    
    # عرض حجم الملف
    file_size = os.path.getsize(output_file)
    print(f"📏 حجم الملف: {file_size:,} بايت ({file_size/1024:.1f} كيلوبايت)")
    
    return output_file

if __name__ == "__main__":
    print("🔍 جاري استخراج جميع أكواد المشروع...")
    output = export_entire_project()
    print(f"\n📌 الخطوات التالية:")
    print(f"1. ارفع ملف '{output}' إلى أي خدمة سحابية:")
    print(f"   - https://gist.github.com/ (للنصوص)")
    print(f"   - Google Drive")
    print(f"   - Dropbox")
    print(f"   - أو أي خدمة مشاركة ملفات")
    print(f"2. أرسل لي الرابط")
    print(f"3. سأقوم بتحليل المشروع كاملاً! 🚀")