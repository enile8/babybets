--
-- Database: `babybets`
--

-- --------------------------------------------------------

--
-- Table structure for table `bets`
--

CREATE TABLE `bets` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `gender` char(1) NOT NULL,
  `date` varchar(30) NOT NULL,
  `lbs` varchar(30) NOT NULL,
  `inches` varchar(30) NOT NULL,
  `notes` text,
  `placed` varchar(30) NOT NULL
) ENGINE=InnoDB;

-- --------------------------------------------------------

--
-- Table structure for table `settings`
--

CREATE TABLE `settings` (
  `id` varchar(10) NOT NULL,
  `value` varchar(10) NOT NULL
) ENGINE=InnoDB;

--
-- Dumping data for table `settings`
--

INSERT INTO `settings` (`id`, `value`) VALUES
('baby_name', 'Unknown'),
('betting', 'open'),
('close_date', '0');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(3) NOT NULL,
  `name` varchar(200) NOT NULL,
  `email` varchar(350) NOT NULL,
  `pwd` varchar(500) NOT NULL,
  `vstr` varchar(500) NOT NULL,
  `ver` int(11) DEFAULT '0'
) ENGINE=InnoDB;

--
-- Indexes for table `bets`
--
ALTER TABLE `bets`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `settings`
--
ALTER TABLE `settings`
  ADD UNIQUE KEY `id` (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `verify_str` (`vstr`);

--
-- AUTO_INCREMENT for table `bets`
--
ALTER TABLE `bets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(3) NOT NULL AUTO_INCREMENT;