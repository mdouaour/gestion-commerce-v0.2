import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export const useDirection = () => {
    const { i18n } = useTranslation();

    useEffect(() => {
        const isRtl = i18n.language === 'ar';
        document.documentElement.dir = isRtl ? 'rtl' : 'ltr';
    }, [i18n.language]);
};
