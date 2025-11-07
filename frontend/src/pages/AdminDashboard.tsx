import React, { useState, useEffect } from 'react';
import { Users, DollarSign, Calendar, TrendingUp, Mail, Phone, CheckCircle, Clock } from 'lucide-react';

interface DashboardStats {
  totalLeads: number;
  assessmentsCompleted: number;
  consultationsBooked: number;
  paymentsCompleted: number;
  totalRevenue: number;
  conversionRate: number;
}

interface Lead {
  id: number;
  name: string;
  email: string;
  company?: string;
  phone?: string;
  crm_system?: string;
  assessment_score?: number;
  consultation_booked: boolean;
  payment_completed: boolean;
  created_at: string;
}

const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalLeads: 0,
    assessmentsCompleted: 0,
    consultationsBooked: 0,
    paymentsCompleted: 0,
    totalRevenue: 0,
    conversionRate: 0,
  });
  
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Simple password protection (in production, use proper auth)
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Change this password to something secure
    if (password === 'unitasa2025') {
      setIsAuthenticated(true);
      fetchDashboardData();
    } else {
      alert('Incorrect password');
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Use the same API URL logic as the rest of the app
      const getApiUrl = () => {
        // If REACT_APP_API_URL is set and it's not the placeholder, use it
        if (process.env.REACT_APP_API_URL && 
            !process.env.REACT_APP_API_URL.includes('your-backend-service.railway.app')) {
          return process.env.REACT_APP_API_URL;
        }
        
        // If we're in production, use relative URLs (same domain)
        if (process.env.NODE_ENV === 'production' || window.location.hostname !== 'localhost') {
          return ''; // Relative URLs will use the same domain
        }
        
        // Development default
        return 'http://localhost:8000';
      };
      
      const apiUrl = getApiUrl();
      console.log('Admin Dashboard API URL:', apiUrl);
      
      // Fetch stats
      const statsResponse = await fetch(`${apiUrl}/api/v1/admin/stats`, {
        headers: {
          'Authorization': `Bearer ${password}`, // Simple auth
        },
      });
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      } else {
        console.error('Stats fetch failed:', statsResponse.status, statsResponse.statusText);
      }

      // Fetch leads
      const leadsResponse = await fetch(`${apiUrl}/api/v1/admin/leads`, {
        headers: {
          'Authorization': `Bearer ${password}`,
        },
      });
      
      if (leadsResponse.ok) {
        const leadsData = await leadsResponse.json();
        setLeads(leadsData.leads || []);
      } else {
        console.error('Leads fetch failed:', leadsResponse.status, leadsResponse.statusText);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Admin Dashboard</h1>
          <form onSubmit={handleLogin}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter admin password"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">Monitor your leads and conversions</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<Users className="w-8 h-8 text-blue-600" />}
            title="Total Leads"
            value={stats.totalLeads}
            bgColor="bg-blue-50"
          />
          <StatCard
            icon={<CheckCircle className="w-8 h-8 text-green-600" />}
            title="Assessments"
            value={stats.assessmentsCompleted}
            bgColor="bg-green-50"
          />
          <StatCard
            icon={<Calendar className="w-8 h-8 text-purple-600" />}
            title="Consultations"
            value={stats.consultationsBooked}
            bgColor="bg-purple-50"
          />
          <StatCard
            icon={<DollarSign className="w-8 h-8 text-yellow-600" />}
            title="Payments"
            value={stats.paymentsCompleted}
            bgColor="bg-yellow-50"
          />
        </div>

        {/* Revenue & Conversion */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Revenue</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  ₹{stats.totalRevenue.toLocaleString('en-IN')}
                </p>
              </div>
              <TrendingUp className="w-12 h-12 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Conversion Rate</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats.conversionRate.toFixed(1)}%
                </p>
              </div>
              <TrendingUp className="w-12 h-12 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Leads Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Recent Leads</h2>
          </div>
          
          {loading ? (
            <div className="p-8 text-center">
              <Clock className="w-8 h-8 text-gray-400 mx-auto mb-2 animate-spin" />
              <p className="text-gray-600">Loading leads...</p>
            </div>
          ) : leads.length === 0 ? (
            <div className="p-8 text-center">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600">No leads yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Lead Info
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      CRM
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                          <div className="text-sm text-gray-500 flex items-center gap-2">
                            <Mail className="w-3 h-3" />
                            {lead.email}
                          </div>
                          {lead.phone && (
                            <div className="text-sm text-gray-500 flex items-center gap-2">
                              <Phone className="w-3 h-3" />
                              {lead.phone}
                            </div>
                          )}
                          {lead.company && (
                            <div className="text-sm text-gray-500">{lead.company}</div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                          {lead.crm_system || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {lead.assessment_score ? (
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            lead.assessment_score >= 70 ? 'bg-green-100 text-green-800' :
                            lead.assessment_score >= 50 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {lead.assessment_score}%
                          </span>
                        ) : (
                          <span className="text-gray-400 text-sm">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col gap-1">
                          {lead.payment_completed && (
                            <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                              💰 Paid
                            </span>
                          )}
                          {lead.consultation_booked && (
                            <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                              📅 Consultation
                            </span>
                          )}
                          {!lead.consultation_booked && !lead.payment_completed && (
                            <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded">
                              🔔 New Lead
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(lead.created_at).toLocaleDateString('en-IN', {
                          day: 'numeric',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Refresh Button */}
        <div className="mt-6 text-center">
          <button
            onClick={fetchDashboardData}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh Data
          </button>
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: number;
  bgColor: string;
}

const StatCard: React.FC<StatCardProps> = ({ icon, title, value, bgColor }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className={`${bgColor} p-3 rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
