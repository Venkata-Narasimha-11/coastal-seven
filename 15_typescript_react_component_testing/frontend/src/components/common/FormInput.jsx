import React from 'react';

export const FormInput = ({
  label,
  id,
  name,
  type = 'text',
  value,
  onChange,
  placeholder,
  error,
  required = false,
  disabled = false,
  helperText,
}) => {
  return (
    <div style={{ marginBottom: '1.25rem' }}>
      {label && (
        <label htmlFor={id || name} className="label">
          {label} {required && <span style={{ color: 'var(--danger)' }}>*</span>}
        </label>
      )}
      <input
        id={id || name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className="input"
        style={error ? { borderColor: 'var(--danger)' } : {}}
      />
      {error && (
        <p style={{ color: 'var(--danger)', fontSize: '0.8rem', marginTop: '0.35rem' }}>
          {error}
        </p>
      )}
      {!error && helperText && (
        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.35rem' }}>
          {helperText}
        </p>
      )}
    </div>
  );
};

export default FormInput;
