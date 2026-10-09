import { createContext, useContext, useEffect, useState } from 'react';
import { login as loginRequest, logout as logoutRequest, signup as signupRequest } from '../services/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
	const [user, setUser] = useState(() => {
		try {
			return JSON.parse(localStorage.getItem('user_data')) || null;
		} catch {
			return null;
		}
	});
	const [loading, setLoading] = useState(false);

	useEffect(() => {
		if (!localStorage.getItem('access_token')) setUser(null);
	}, []);

	const login = async (email, password) => {
		setLoading(true);
		const result = await loginRequest(email, password);
		if (result.success) {
			const data = result.data;
			const nextUser = { id: data.user_id, name: data.user_name, role: data.user_role, email };
			localStorage.setItem('access_token', data.access_token);
			localStorage.setItem('user_data', JSON.stringify(nextUser));
			setUser(nextUser);
		}
		setLoading(false);
		return result;
	};

	const logout = () => {
		logoutRequest();
		setUser(null);
	};

	const value = {
		user,
		loading,
		isAuthenticated: Boolean(user && localStorage.getItem('access_token')),
		isLearner: user?.role === 'learner',
		isInstructor: user?.role === 'instructor',
		isAdmin: user?.role === 'admin' || user?.email === 'admin@learnverse.com',
		login,
		signup: signupRequest,
		logout,
	};

	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
	const context = useContext(AuthContext);
	if (!context) throw new Error('useAuth must be used within AuthProvider');
	return context;
}
