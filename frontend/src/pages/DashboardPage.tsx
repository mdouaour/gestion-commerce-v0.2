import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

const DashboardPage = () => {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="p-8">
      <div className="flex justify-between">
        <h1 className="text-3xl font-bold">{t('dashboard.title')}</h1>
        <div className="flex items-center space-x-2">
            <button onClick={() => changeLanguage('fr')} className="px-2 py-1 text-sm bg-gray-200 rounded">FR</button>
            <button onClick={() => changeLanguage('ar')} className="px-2 py-1 text-sm bg-gray-200 rounded">AR</button>
        </div>
      </div>
      <p className="mt-2 text-lg">
        {t('dashboard.welcomeMessage', { username: user?.username })}
      </p>
      <p>{t('dashboard.roleInfo', { role: user?.role })}</p>
      
      <button 
        onClick={logout}
        className="px-4 py-2 mt-4 font-bold text-white bg-red-500 rounded hover:bg-red-700"
      >
        {t('dashboard.logoutButton')}
      </button>
    </div>
  );
};

export default DashboardPage;
