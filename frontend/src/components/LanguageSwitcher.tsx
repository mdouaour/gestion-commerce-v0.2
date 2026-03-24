import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

const languages = [
    { code: 'fr', name: 'Français' },
    { code: 'ar', name: 'العربية' },
];

const LanguageSwitcher = () => {
    const { i18n } = useTranslation();

    const changeLanguage = (lng: string) => {
        i18n.changeLanguage(lng);
    };

    return (
        <div className="relative">
            <div className="flex items-center space-x-4">
                <Globe className="w-5 h-5 text-gray-600" />
                {languages.map((lng) => (
                    <button
                        key={lng.code}
                        onClick={() => changeLanguage(lng.code)}
                        className={`px-3 py-1 text-sm rounded-md ${i18n.language === lng.code ? 'font-bold text-white bg-blue-600' : 'bg-gray-200'}`}
                    >
                        {lng.name}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default LanguageSwitcher;
