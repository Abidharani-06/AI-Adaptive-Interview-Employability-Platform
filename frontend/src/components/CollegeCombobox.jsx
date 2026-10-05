import React, { useState, useRef, useEffect } from 'react';
import { Search, ChevronDown, Check, Building2, X } from 'lucide-react';
import { TAMIL_NADU_COLLEGES } from '../data/tamilNaduColleges';

export default function CollegeCombobox({
  value,
  onChange,
  onOtherSelected,
  placeholder = "Search college or university in Tamil Nadu...",
  required = false
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const containerRef = useRef(null);
  const listRef = useRef(null);

  // Filtered colleges list based on search query
  const filteredColleges = TAMIL_NADU_COLLEGES.filter(col =>
    col.toLowerCase().includes(searchTerm.toLowerCase().trim())
  );

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (collegeName) => {
    if (collegeName === "Other (Specify institution manually)") {
      onChange("Other");
      if (onOtherSelected) onOtherSelected(true);
    } else {
      onChange(collegeName);
      if (onOtherSelected) onOtherSelected(false);
    }
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleKeyDown = (e) => {
    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        setIsOpen(true);
        e.preventDefault();
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex(prev => (prev < filteredColleges.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex(prev => (prev > 0 ? prev - 1 : filteredColleges.length - 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (highlightedIndex >= 0 && highlightedIndex < filteredColleges.length) {
        handleSelect(filteredColleges[highlightedIndex]);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div ref={containerRef} style={{ position: 'relative', width: '100%' }}>
      {/* Selected Box / Trigger */}
      <div
        tabIndex={0}
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '11px 14px',
          backgroundColor: '#111827',
          border: isOpen ? '1.5px solid #6366f1' : '1px solid #374151',
          borderRadius: '10px',
          color: value ? '#f8fafc' : '#9ca3af',
          cursor: 'pointer',
          fontSize: '13.5px',
          transition: 'all 0.15s ease',
          boxShadow: isOpen ? '0 0 0 3px rgba(99, 102, 241, 0.15)' : 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
          <Building2 size={16} color={value ? '#818cf8' : '#6b7280'} style={{ flexShrink: 0 }} />
          <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {value === "Other" ? "Other (Specified manually)" : value || placeholder}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {value && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onChange('');
                if (onOtherSelected) onOtherSelected(false);
              }}
              style={{
                color: '#9ca3af',
                padding: '2px',
                display: 'flex',
                borderRadius: '4px'
              }}
              title="Clear selection"
            >
              <X size={14} />
            </button>
          )}
          <ChevronDown
            size={16}
            color="#9ca3af"
            style={{
              transform: isOpen ? 'rotate(180deg)' : 'none',
              transition: 'transform 0.2s ease'
            }}
          />
        </div>
      </div>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            right: 0,
            backgroundColor: '#1f2937',
            border: '1px solid #374151',
            borderRadius: '12px',
            boxShadow: '0 12px 28px rgba(0, 0, 0, 0.45)',
            zIndex: 100,
            overflow: 'hidden',
            maxHeight: '320px',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          {/* Search Input Filter */}
          <div
            style={{
              padding: '10px',
              borderBottom: '1px solid #374151',
              backgroundColor: '#111827',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <Search size={15} color="#9ca3af" />
            <input
              type="text"
              autoFocus
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setHighlightedIndex(0);
              }}
              onKeyDown={handleKeyDown}
              placeholder="Type to filter colleges..."
              style={{
                width: '100%',
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#f8fafc',
                fontSize: '13px'
              }}
            />
          </div>

          {/* College Options List */}
          <div
            ref={listRef}
            style={{
              overflowY: 'auto',
              maxHeight: '260px',
              padding: '6px'
            }}
          >
            {filteredColleges.length === 0 ? (
              <div
                style={{
                  padding: '16px',
                  textAlign: 'center',
                  color: '#9ca3af',
                  fontSize: '13px'
                }}
              >
                No matching college found.
                <div style={{ marginTop: '8px' }}>
                  <button
                    type="button"
                    onClick={() => handleSelect("Other (Specify institution manually)")}
                    style={{
                      color: '#818cf8',
                      fontWeight: 600,
                      fontSize: '12.5px',
                      textDecoration: 'underline'
                    }}
                  >
                    Select "Other" to enter manually
                  </button>
                </div>
              </div>
            ) : (
              filteredColleges.map((col, idx) => {
                const isSelected = value === col || (value === "Other" && col.startsWith("Other"));
                const isHighlighted = idx === highlightedIndex;

                return (
                  <div
                    key={col}
                    onClick={() => handleSelect(col)}
                    onMouseEnter={() => setHighlightedIndex(idx)}
                    style={{
                      padding: '9px 12px',
                      borderRadius: '8px',
                      fontSize: '13px',
                      color: isSelected ? '#a5b4fc' : '#f3f4f6',
                      backgroundColor: isHighlighted
                        ? 'rgba(99, 102, 241, 0.15)'
                        : isSelected
                        ? 'rgba(99, 102, 241, 0.08)'
                        : 'transparent',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'background 0.1s ease',
                      fontWeight: isSelected ? 600 : 400
                    }}
                  >
                    <span style={{ lineHeight: 1.4 }}>{col}</span>
                    {isSelected && <Check size={14} color="#818cf8" style={{ flexShrink: 0 }} />}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
