/**
 * Country Selector Component
 */

import { Select, Spin } from 'antd';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { Country } from '../../types/models.types';

interface CountrySelectorProps {
  value: number | null;
  onChange: (value: number | null) => void;
}

function CountrySelector({ value, onChange }: CountrySelectorProps) {
  const { data: countries, isLoading } = useQuery({
    queryKey: QUERY_KEYS.countries,
    queryFn: async () => {
      const response = await apiClient.get<Country[]>(API_ENDPOINTS.countries);
      return response.data;
    },
  });
  
  return (
    <div>
      <label className="input-label">Step 2: Select Target Country</label>
      <Select
        showSearch
        placeholder="Select target country"
        value={value}
        onChange={onChange}
        loading={isLoading}
        style={{ width: '100%' }}
        size="large"
        notFoundContent={isLoading ? <Spin size="small" /> : 'No countries found'}
        filterOption={(input, option) =>
          (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
        }
        options={countries?.map(country => ({
          label: `${country.name} (${country.iso_code})`,
          value: country.id,
        })) || []}
      />
    </div>
  );
}

export default CountrySelector;


