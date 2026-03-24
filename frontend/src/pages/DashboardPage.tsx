import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../components/LanguageSwitcher';

const DashboardPage = () => {
  const { t } = useTranslation();
  const { user, logout } = useAuth();

  return (
    <div className="p-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">{t('dashboard.title')}</h1>
        <LanguageSwitcher />
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
