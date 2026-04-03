# backend/tests/test_gemini.py

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.gemini import GeminiClient
from typing import List, Dict

test_candidates: List[Dict] = [
    {
        "name": "john doe",
        "category": "Blockchain",
        "role": "Senior Smart Contract Developer",
        "skills": ["Solidity", "Rust", "Web3.py", "Hardhat", "Foundry"],
        "experience_years": 5,
        "location": "TP.HCM",
        "education": "Helsinki University - MSc Computer Science",
        "languages": ["finnish", "english"],
        "certifications": ["Certified Solidity Developer"],
        "availability": "immediate",
        "summary": "Experienced blockchain developer with a strong background in smart contract development using Solidity and Rust. Proficient in using Hardhat and Foundry for testing and deployment. Passionate about building secure and efficient decentralized applications."
    },
    {
        "name": "jane smith",
        "category": "Blockchain",
        "role": "Smart Contract Engineer",
        "skills": ["Solidity", "JavaScript", "Truffle", "Ganache"],
        "experience_years": 3,
        "location": "Hà Nội",
        "education": "Vietnam National University - BSc Computer Science",
        "languages": ["vietnamese", "english"],
        "certifications": ["Ethereum Developer Certification"],
        "availability": "2 weeks notice",
        "summary": "Skilled smart contract engineer with 3 years of experience in developing and deploying Ethereum-based applications. Adept at using Truffle and Ganache for development and testing. Committed to writing clean, efficient, and secure code."
    },
    {
        "name": "alice nguyen",
        "category": "Blockchain",
        "role": "Full Stack Blockchain Developer",
        "skills": ["Solidity", "TypeScript", "Next.js", "Hardhat", "Foundry"],
        "experience_years": 4,
        "location": "Đà Nẵng",
        "education": "Da Nang University of Technology - BEng Software Engineering",
        "languages": ["vietnamese", "english"],
        "certifications": ["Full Stack Blockchain Developer"],
        "availability": "1 month notice",
        "summary": "Versatile full stack blockchain developer with expertise in both front-end and back-end development. Experienced in building decentralized applications using Solidity, TypeScript, and Next.js. Proficient in Hardhat and Foundry for smart contract development and testing."
    },
    {
        "name": "bob tran",
        "category": "Blockchain",
        "role": "Junior Smart Contract Developer",
        "skills": ["Solidity", "Python", "Brownie"],
        "experience_years": 1,
        "location": "Hải Phòng",
        "education": "Hai Phong University - BSc Information Technology",
        "languages": ["vietnamese", "english"],
        "certifications": ["Junior Blockchain Developer"],
        "availability": "immediate",
        "summary": "Enthusiastic junior smart contract developer with a solid foundation in Solidity and Python. Experienced in using Brownie for smart contract development and testing. Eager to contribute to innovative blockchain projects and grow professionally."
    },
    {
        "name": "charlie pham",
        "category": "Blockchain",
        "role": "Smart Contract Auditor",
        "skills": ["Solidity", "Security Auditing", "MythX", "Slither"],
        "experience_years": 6,
        "location": "Cần Thơ",
        "education": "Can Tho University - MSc Information Security",
        "languages": ["vietnamese", "english"],
        "certifications": ["Certified Blockchain Security Professional"],
        "availability": "3 weeks notice",
        "summary": "Experienced smart contract auditor with a strong focus on security and best practices. Proficient in using tools like MythX and Slither for auditing Solidity contracts. Dedicated to ensuring the safety and reliability of blockchain applications."
    },
    {
        "name": "diana le",
        "category": "Blockchain",
        "role": "Blockchain Developer",
        "skills": ["Solidity", "Go", "Web3.js", "Hardhat"],
        "experience_years": 2,
        "location": "Nha Trang",
        "education": "Nha Trang University - BSc Computer Science",
        "languages": ["vietnamese", "english"],
        "certifications": ["Blockchain Development Certification"],
        "availability": "immediate",
        "summary": "Motivated blockchain developer with experience in building decentralized applications using Solidity and Go. Skilled in using Web3.js and Hardhat for smart contract interaction and development. Passionate about leveraging blockchain technology to create innovative solutions."
    },
    {
        "name": "edward hoang",
        "category": "Blockchain",
        "role": "Senior Blockchain Engineer",
        "skills": ["Solidity", "C++", "EOSIO", "Hardhat", "Foundry"],
        "experience_years": 7,
        "location": "Vũng Tàu",
        "education": "Vung Tau University - MSc Software Engineering",
        "languages": ["vietnamese", "english"],
        "certifications": ["Advanced Blockchain Engineer"],
        "availability": "1 month notice",
        "summary": "Seasoned blockchain engineer with extensive experience in smart contract development and blockchain architecture. Proficient in Solidity, C++, and EOSIO, with a strong command of Hardhat and Foundry for development and testing. Committed to delivering high-quality blockchain solutions that meet industry standards."
    },
    {
        "name": "fiona vu",
        "category": "Blockchain",
        "role": "Smart Contract Developer",
        "skills": ["Solidity", "Java", "Web3j", "Truffle"],
        "experience_years": 3,
        "location": "Huế",
        "education": "Hue University - BSc Information Technology",
        "languages": ["vietnamese", "english"],
        "certifications": ["Smart Contract Development Certification"],
        "availability": "2 weeks notice",
        "summary": "Proficient smart contract developer with a background in Java and blockchain technologies. Experienced in using Web3j and Truffle for Ethereum development. Focused on creating efficient and secure smart contracts that align with project requirements."
    },
    {
        "name": "george phan",
        "category": "Blockchain",
        "role": "Blockchain Solutions Architect",
        "skills": ["Solidity", "Architecture Design", "Hyperledger", "Hardhat"],
        "experience_years": 8,
        "location": "Quảng Ninh",
        "education": "Quang Ninh University - MSc Computer Science",
        "languages": ["vietnamese", "english"],
        "certifications": ["Certified Blockchain Solutions Architect"],
        "availability": "1 month notice",
        "summary": "Expert blockchain solutions architect with a deep understanding of blockchain technologies and architecture design. Skilled in Solidity and Hyperledger, with extensive experience in using Hardhat for development. Dedicated to designing robust and scalable blockchain solutions that drive business value."
    },
]

job_query = "Looking for a skilled blockchain developer with expertise in Solidity and experience in building decentralized applications. The ideal candidate should have a strong background in smart contract development, proficiency in using development frameworks like Hardhat or Truffle, and a passion for blockchain technology."

if __name__ == "__main__":
    client = GeminiClient()
    result = client.generate_text(job_query, test_candidates)
    print("\nn\n")
    print(result)