# Patches the generated Android project: release signing from env, version code from CI run number.
import os, re
p = 'android/app/build.gradle'
s = open(p).read()
code = os.environ.get('VERSION_CODE', '1')
s = re.sub(r'versionCode\s+\d+', f'versionCode {code}', s)
s = re.sub(r'versionName\s+"[^"]*"', f'versionName "1.0.{code}"', s)
if os.environ.get('KEYSTORE_FILE') and 'signingConfigs' not in s:
    s = s.replace('buildTypes {', '''signingConfigs {
        release {
            storeFile file(System.getenv("KEYSTORE_FILE"))
            storePassword System.getenv("KEYSTORE_PASSWORD")
            keyAlias System.getenv("KEY_ALIAS")
            keyPassword System.getenv("KEY_PASSWORD")
        }
    }
    buildTypes {''', 1)
    s = s.replace('release {\n            minifyEnabled', 'release {\n            signingConfig signingConfigs.release\n            minifyEnabled', 1)
open(p, 'w').write(s)
print(s[s.find('defaultConfig'):s.find('defaultConfig')+500])
