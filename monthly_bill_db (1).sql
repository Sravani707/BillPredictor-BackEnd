-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3307
-- Generation Time: Mar 20, 2026 at 04:37 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `monthly_bill_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE `categories` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `category_name` varchar(100) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id`, `user_id`, `category_name`, `created_at`) VALUES
(1, 1, 'Rent', '2026-03-09 04:53:42'),
(2, 1, 'Food', '2026-03-09 04:53:42'),
(3, 1, 'Travel', '2026-03-09 04:53:42'),
(4, 1, 'Shopping', '2026-03-09 04:53:42'),
(5, 1, 'Bills', '2026-03-09 04:53:42'),
(6, 1, 'Education', '2026-03-09 04:53:42'),
(7, 1, 'Health', '2026-03-09 04:53:42'),
(8, 1, 'Groceries', '2026-03-09 04:53:42'),
(9, 1, 'Subscriptions', '2026-03-09 04:53:42'),
(10, 1, 'Others', '2026-03-09 04:53:42');

-- --------------------------------------------------------

--
-- Table structure for table `events`
--

CREATE TABLE `events` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `event_name` varchar(200) DEFAULT NULL,
  `event_date` date DEFAULT NULL,
  `estimated_cost` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `events`
--

INSERT INTO `events` (`id`, `user_id`, `event_name`, `event_date`, `estimated_cost`, `created_at`) VALUES
(4, 1, 'nanna bdy', '2026-04-06', 500.00, '2026-03-09 05:09:29'),
(5, 1, 'anna bdy', '2026-11-27', 1500.00, '2026-03-09 05:09:29'),
(8, 2, 'sravs bdy', '2026-10-22', 5000.00, '2026-03-09 05:09:29'),
(13, 2, 'Ugadi', '2026-06-18', 1000.00, '2026-03-11 03:01:01');

-- --------------------------------------------------------

--
-- Table structure for table `event_savings`
--

CREATE TABLE `event_savings` (
  `id` int(11) NOT NULL,
  `event_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `month_year` varchar(20) DEFAULT NULL,
  `required_amount` decimal(10,2) DEFAULT NULL,
  `saved` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `event_savings`
--

INSERT INTO `event_savings` (`id`, `event_id`, `user_id`, `month_year`, `required_amount`, `saved`) VALUES
(1, 13, 2, 'March 2026', 333.33, 1),
(2, 13, 2, 'April 2026', 333.33, 0),
(3, 13, 2, 'May 2026', 333.33, 0);

-- --------------------------------------------------------

--
-- Table structure for table `expenses`
--

CREATE TABLE `expenses` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `expense_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `expenses`
--

INSERT INTO `expenses` (`id`, `user_id`, `category_id`, `amount`, `expense_date`) VALUES
(5, 2, 1, 9000.00, '2025-02-10'),
(6, 2, 2, 2000.00, '2025-11-05'),
(7, 2, 4, 500.00, '2026-03-02'),
(8, 2, 1, 7000.00, '2026-03-02'),
(9, 2, 2, 1500.00, '2026-03-02'),
(11, 1, 3, 1500.00, '2026-03-02'),
(12, 1, 1, 3500.00, '2026-01-05'),
(13, 1, 2, 1200.00, '2026-01-08'),
(14, 2, 3, 4000.00, '2026-01-12'),
(15, 2, 4, 5000.00, '2026-01-18'),
(17, 1, 1, 4200.00, '2026-02-04'),
(18, 1, 2, 1500.00, '2026-02-09'),
(19, 2, 3, 4800.00, '2026-02-13'),
(20, 2, 4, 6000.00, '2026-02-20'),
(21, 2, 5, 4503.00, '2026-02-26'),
(22, 2, 7, 550.00, '2026-03-09'),
(23, 2, 9, 200.00, '2026-03-10');

-- --------------------------------------------------------

--
-- Table structure for table `income`
--

CREATE TABLE `income` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `income`
--

INSERT INTO `income` (`id`, `user_id`, `amount`, `date`, `created_at`) VALUES
(2, 2, 20000.00, '2026-03-10', '2026-03-10 03:55:36'),
(3, 2, 200.00, '2026-03-10', '2026-03-10 04:05:30');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `otp` varchar(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `created_at`, `otp`) VALUES
(1, 'Test User', 'test@example.com', '123456', '2026-03-09 04:44:54', NULL),
(2, 'Sravs_1962', 'sravani.ch2004@gmail.com', 'Saveetha@', '2026-03-09 05:00:36', NULL),
(3, NULL, 'ranjithavangaveeti@gmail.com', 'Ranjitha@', '2026-03-09 05:20:02', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `events`
--
ALTER TABLE `events`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `event_savings`
--
ALTER TABLE `event_savings`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `expenses`
--
ALTER TABLE `expenses`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `income`
--
ALTER TABLE `income`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `events`
--
ALTER TABLE `events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `event_savings`
--
ALTER TABLE `event_savings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `expenses`
--
ALTER TABLE `expenses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `income`
--
ALTER TABLE `income`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `categories`
--
ALTER TABLE `categories`
  ADD CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `events`
--
ALTER TABLE `events`
  ADD CONSTRAINT `events_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `expenses`
--
ALTER TABLE `expenses`
  ADD CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `expenses_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
